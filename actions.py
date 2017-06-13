# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import yaml
from socket import getfqdn

from docker import Client

from clusterdock.cluster import Cluster, Node, NodeGroup
from clusterdock.docker_utils import (get_host_port_binding, is_image_available_locally,
                                      pull_image)
from clusterdock.utils import wait_for_port_open

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def start(args):
    primary_node_image = "{0}/{1}/clusterdock:mapr{2}_primary-node".format(
        args.registry_url, args.namespace,
        args.mapr_version
    )

    secondary_node_image = "{0}/{1}/clusterdock:mapr{2}_secondary-node".format(
        args.registry_url, args.namespace,
        args.mapr_version
    )

    for image in [primary_node_image, secondary_node_image]:
        if args.always_pull or args.only_pull or not is_image_available_locally(image):
            logger.info("Pulling image %s. This might take a little while ...", image)
            pull_image(image)

    if args.only_pull:
        return

    MCS_SERVER_PORT = 8443

    node_disks = yaml.load(args.node_disks)

    # MapR-FS needs each fileserver node to have a disk allocated for it, so fail fast if the
    # node disks map is missing any nodes.
    if set(args.primary_node + args.secondary_nodes) != set(node_disks.keys()):
        raise Exception('Not all nodes are accounted for in the --node-disks dictionary')

    primary_node = Node(hostname=args.primary_node[0],
                        network=args.network,
                        image=primary_node_image,
                        ports=[MCS_SERVER_PORT],
                        devices=node_disks.get(args.primary_node[0]))

    secondary_nodes = [Node(hostname=hostname,
                            network=args.network,
                            image=secondary_node_image,
                            devices=node_disks.get(hostname))
                       for hostname in args.secondary_nodes]

    secondary_node_group = NodeGroup(name='secondary', nodes=secondary_nodes)
    node_groups = [NodeGroup(name='primary', nodes=[primary_node]),
                   secondary_node_group]

    cluster = Cluster(topology='mapr', node_groups=node_groups, network_name=args.network)
    cluster.start()

    logger.info('Generating new UUIDs ...')
    cluster.ssh('/opt/mapr/server/mruuidgen > /opt/mapr/hostid')

    for node in cluster:
        configure_command = ('/opt/mapr/server/configure.sh -C {0} -Z {0} -RM {0} -HS {0} '
                             '-u mapr -g mapr -D {1} '
                             '-defaultdb maprdb'.format(primary_node.fqdn,
                                                        ','.join(node_disks.get(node.hostname))))
        logger.info('Running %s on %s ...', configure_command, node.hostname)
        node.ssh(configure_command)

    logger.info('Waiting for MapR Control System server to come online ...')
    mcs_server_startup_time = wait_for_port_open(primary_node.ip_address,
                                                MCS_SERVER_PORT, timeout_sec=180)
    logger.info("Detected MapR Control System server after %.2f seconds.", mcs_server_startup_time)
    mcs_server_host_port = get_host_port_binding(primary_node.container_id,
                                                 MCS_SERVER_PORT)


    logger.info('Creating /apps/spark directory on %s ...', primary_node.hostname)
    spark_directory_command = ['sudo -u mapr hadoop fs -mkdir -p /apps/spark',
                               'sudo -u mapr hadoop fs -chmod 777 /apps/spark']
    primary_node.ssh('; '.join(spark_directory_command))

    logger.info('Creating MapR sample Stream named /sample-stream on %s ...', primary_node.hostname)
    primary_node.ssh('sudo -u mapr maprcli stream create -path /sample-stream '
                     '-produceperm p -consumeperm p -topicperm p')

    logger.info('Creating sdc user directory in MapR-FS ...')
    create_sdc_user_directory_command = ['sudo -u mapr hadoop fs -mkdir -p /user/sdc',
                                         'sudo -u mapr hadoop fs -chown sdc:sdc /user/sdc']
    primary_node.ssh('; '.join(create_sdc_user_directory_command))

    logger.info("MapR Control System server is now accessible at https://%s:%s",
                getfqdn(), mcs_server_host_port)
