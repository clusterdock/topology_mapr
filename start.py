# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import tempfile
import yaml
from socket import getfqdn, socket

from clusterdock.models import Cluster, Node
from clusterdock.utils import wait_for_condition

DEFAULT_NAMESPACE = 'clusterdock'
DEFAULT_SDC_REPO = 'https://s3-us-west-2.amazonaws.com/archives.streamsets.com/datacollector/'
EARLIEST_MAPR_VERSION_WITH_LICENSE_AND_CENTOS_7 = (6, 0, 0)
# For MEP 4.0 onwards, MAPR_MEP_VERSION env. variable is needed by setup_mapr script.
EARLIEST_MEP_VERSION_FOR_SETUP_MAPR_SCRIPT = (4, 0)
MAPR_CONFIG_DIR = '/opt/mapr/conf'
MAPR_SERVERTICKET_FILE = 'maprserverticket'
MCS_SERVER_PORT = 8443
SECURE_CONFIG_CONTAINER_DIR = '/etc/clusterdock/secure'
SSL_KEYSTORE_FILE = 'ssl_keystore'
SSL_TRUSTSTORE_FILE = 'ssl_truststore'

SECURE_FILES = [
    MAPR_SERVERTICKET_FILE,
    SSL_KEYSTORE_FILE,
    SSL_TRUSTSTORE_FILE
]


logger = logging.getLogger('clusterdock.{}'.format(__name__))


def main(args):
    if args.license_url and not args.license_credentials:
        raise Exception('--license-credentials is a required argument if --license-url is provided.')

    image_prefix = '{}/{}/clusterdock:mapr{}'.format(args.registry,
                                                     args.namespace or DEFAULT_NAMESPACE,
                                                     args.mapr_version)
    if args.mep_version:
        image_prefix = '{}_mep{}'.format(image_prefix, args.mep_version)
    primary_node_image = '{}_{}'.format(image_prefix, 'primary-node')
    secondary_node_image = '{}_{}'.format(image_prefix, 'secondary-node')

    node_disks = yaml.load(args.node_disks)

    # MapR-FS needs each fileserver node to have a disk allocated for it, so fail fast if the
    # node disks map is missing any nodes.
    if set(args.primary_node + args.secondary_nodes) != set(node_disks):
        raise Exception('Not all nodes are accounted for in the --node-disks dictionary')

    primary_node = Node(hostname=args.primary_node[0],
                        group='primary',
                        image=primary_node_image,
                        ports=[{MCS_SERVER_PORT: MCS_SERVER_PORT}
                               if args.predictable
                               else MCS_SERVER_PORT],
                        devices=node_disks.get(args.primary_node[0]),
                        # Secure cluster needs the ticket to execute rest of commands
                        # after cluster start.
                        environment=['MAPR_TICKETFILE_LOCATION=/opt/mapr/conf/mapruserticket']
                        if args.secure else [])

    secondary_nodes = [Node(hostname=hostname,
                            group='secondary',
                            image=secondary_node_image,
                            devices=node_disks.get(hostname))
                       for hostname in args.secondary_nodes]

    cluster = Cluster(primary_node, *secondary_nodes)

    if args.secure:
        secure_config_host_dir = os.path.expanduser(args.secure_config_directory)
        volumes = [{secure_config_host_dir: SECURE_CONFIG_CONTAINER_DIR}]
        for node in cluster.nodes:
            node.volumes.extend(volumes)

    # MapR versions 6.0.0 onwards use CentOS 7 which needs following settings.
    mapr_version_tuple = tuple(int(i) for i in args.mapr_version.split('.'))
    if mapr_version_tuple >= EARLIEST_MAPR_VERSION_WITH_LICENSE_AND_CENTOS_7:
        for node in cluster.nodes:
            node.volumes.append({'/sys/fs/cgroup': '/sys/fs/cgroup'})
            temp_dir_name = tempfile.mkdtemp()
            logger.debug('Created temporary directory %s', temp_dir_name)
            node.volumes.append({temp_dir_name: '/run'})
    cluster.primary_node = primary_node
    cluster.start(args.network, pull_images=args.always_pull)

    logger.info('Generating new UUIDs ...')
    cluster.execute('/opt/mapr/server/mruuidgen > /opt/mapr/hostid')

    if not args.secure:
        logger.info('Configuring the cluster ...')
        for node in cluster:
            configure_command = ('/opt/mapr/server/configure.sh -C {0} -Z {0} -RM {0} -HS {0} '
                                 '-u mapr -g mapr -D {1}'.format(
                                     primary_node.fqdn,
                                     ','.join(node_disks.get(node.hostname))
                                 ))
            node.execute("bash -c '{}'".format(configure_command))
    else:
        logger.info('Configuring native security for the cluster ...')
        configure_command = ('/opt/mapr/server/configure.sh -secure -genkeys -C {0} -Z {0} -RM {0} -HS {0} '
                             '-u mapr -g mapr -D {1}'.format(
                                 primary_node.fqdn,
                                 ','.join(node_disks.get(primary_node.hostname))
                             ))
        source_files = ['{}/{}'.format(MAPR_CONFIG_DIR, file) for file in SECURE_FILES]
        commands = [configure_command,
                    'chmod 600 {}/{}'.format(MAPR_CONFIG_DIR, SSL_KEYSTORE_FILE),
                    'cp -f {src} {dest_dir}'.format(src=' '.join(source_files),
                                                    dest_dir=SECURE_CONFIG_CONTAINER_DIR)]
        primary_node.execute(' && '.join(commands))
        for node in secondary_nodes:
            source_files = ['{}/{}'.format(SECURE_CONFIG_CONTAINER_DIR, file)
                            for file in SECURE_FILES]
            configure_command = ('/opt/mapr/server/configure.sh -secure -C {0} -Z {0} -RM {0} -HS {0} '
                                 '-u mapr -g mapr -D {1}'.format(
                                     primary_node.fqdn,
                                     ','.join(node_disks.get(node.hostname))
                                 ))
            commands = ['cp -f {src} {dest_dir}'.format(src=' '.join(source_files),
                                                        dest_dir=MAPR_CONFIG_DIR),
                        configure_command]
            node.execute(' && '.join(commands))

    logger.info('Waiting for MapR Control System server to come online ...')

    def condition(address, port):
        return socket().connect_ex((address, port)) == 0

    def success(time):
        logger.info('MapR Control System server is online after %s seconds.', time)

    def failure(timeout):
        raise TimeoutError('Timed out after {} seconds waiting '
                           'for MapR Control System server to come online.'.format(timeout))
    wait_for_condition(condition=condition,
                       condition_args=[primary_node.ip_address, MCS_SERVER_PORT],
                       time_between_checks=3, timeout=180, success=success, failure=failure)
    mcs_server_host_port = primary_node.host_ports.get(MCS_SERVER_PORT)

    logger.info('Creating /apps/spark directory on %s ...', primary_node.hostname)
    spark_directory_command = ['hadoop fs -mkdir -p /apps/spark',
                               'hadoop fs -chmod 777 /apps/spark']
    primary_node.execute("bash -c '{}'".format('; '.join(spark_directory_command)))

    logger.info('Creating MapR sample Stream named /sample-stream on %s ...', primary_node.hostname)
    primary_node.execute('maprcli stream create -path /sample-stream '
                         '-produceperm p -consumeperm p -topicperm p')

    if mapr_version_tuple >= EARLIEST_MAPR_VERSION_WITH_LICENSE_AND_CENTOS_7 and args.license_url:
        license_commands = ['curl --user {} {} > /tmp/lic'.format(args.license_credentials,
                                                                  args.license_url),
                            '/opt/mapr/bin/maprcli license add -license /tmp/lic -is_file true',
                            'rm -rf /tmp/lic']
        logger.info('Applying license ...')
        primary_node.execute(' && '.join(license_commands))

    if not args.dont_register_gateway:
        logger.info('Registering gateway with the cluster ...')
        register_gateway_commands = ["cat /opt/mapr/conf/mapr-clusters.conf | egrep -o '^[^ ]* '"
                                     ' > /tmp/cluster-name',
                                     'maprcli cluster gateway set -dstcluster $(cat '
                                     '/tmp/cluster-name) -gateways {}'.format(primary_node.fqdn),
                                     'rm /tmp/cluster-name']
        primary_node.execute(' && '.join(register_gateway_commands))

    logger.info('Creating sdc user directory in MapR-FS ...')
    create_sdc_user_directory_command = ['sudo -u mapr hadoop fs -mkdir -p /user/sdc',
                                         'sudo -u mapr hadoop fs -chown sdc:sdc /user/sdc']
    primary_node.execute('; '.join(create_sdc_user_directory_command))

    if args.sdc_version:
        logger.info('Installing StreamSets DataCollector version %s ...', args.sdc_version)
        _install_streamsets_datacollector(primary_node, args.sdc_version,
                                          args.mapr_version, args.mep_version)
        logger.info('StreamSets DataCollector version %s is installed using rpm. '
                    'Install additional stage libraries using rpm ...', args.sdc_version)

    logger.info('MapR Control System server is now accessible at https://%s:%s',
                getfqdn(), mcs_server_host_port)


# Returns wget commands and rpm package names for all the rpm packages needed.
# These lists depend on the SDC version, MapR version and MEP version.
def _gather_wget_commands_and_rpm_names(whole_sdc_version, mapr_version, mep_version):
    result_rpms = []
    sdc_version = whole_sdc_version.rsplit('-RC')[0]
    sdc_rpm = 'streamsets-datacollector-{}-1.noarch.rpm'.format(sdc_version)
    result_rpms.append(sdc_rpm)
    name = 'streamsets-datacollector-mapr_{mapr_version}-lib-{sdc_version}-1.noarch.rpm'
    sdc_mapr_rpm = name.format(sdc_version=sdc_version,
                               mapr_version='_'.join(mapr_version.split('.')[:2]))
    result_rpms.append(sdc_mapr_rpm)

    result_wgets = []
    el_part = ''
    if sdc_version.startswith('3'):
        el_part = 'el7/' if mapr_version.startswith('6') else 'el6/'
    base_url = '{sdc_repo}{sdc_ver}/rpm/{el_part}'.format(sdc_repo=DEFAULT_SDC_REPO,
                                                          sdc_ver=whole_sdc_version,
                                                          el_part=el_part)

    # RPM for SDC.
    result_wgets.append('wget -q {base_url}{sdc_rpm}'.format(base_url=base_url, sdc_rpm=sdc_rpm))
    # RPM for MapR stage library.
    result_wgets.append('wget -q {base_url}{sdc_mapr_rpm}'.format(base_url=base_url,
                                                                  sdc_mapr_rpm=sdc_mapr_rpm))
    # RPM for MEP stage library for MapR 6.
    if mapr_version.startswith('6'):
        mep_rpm_name = 'streamsets-datacollector-mapr_{}-mep{}-lib-{}-1.noarch.rpm'
        mep_rpm = mep_rpm_name.format('_'.join(mapr_version.split('.')[:2]),
                                      mep_version[:1],
                                      sdc_version)
        result_wgets.append('wget -q {base_url}{mep_rpm}'.format(base_url=base_url,
                                                                 mep_rpm=mep_rpm))
        result_rpms.append(mep_rpm)
    # RPM for Spark 2.1 stage library for MapR 5.2.2.
    if mapr_version == '5.2.2' and mep_version.startswith('3'):
        spark_rpm_name = 'streamsets-datacollector-mapr_spark_2_1_mep_{}-lib-{}-1.noarch.rpm'
        spark_rpm = spark_rpm_name.format('_'.join(mep_version.split('.')[:2]), sdc_version)
        result_wgets.append('wget -q {base_url}{spark_rpm}'.format(base_url=base_url,
                                                                   spark_rpm=spark_rpm))
        result_rpms.append(spark_rpm)

    return result_wgets, result_rpms


# Installation of SDC happens in following major steps:
# Fetch and install all the rpm packages for the SDC core and MapR stage-libs
# Run the script to setup MapR
# Start SDC service
def _install_streamsets_datacollector(primary_node, sdc_version, mapr_version, mep_version):
    primary_node.execute('JAVA_HOME=/usr/java/jdk1.8.0_131')
    primary_node.execute('cd /opt/')
    wget_commands, rpm_names = _gather_wget_commands_and_rpm_names(sdc_version, mapr_version, mep_version)
    primary_node.execute('; '.join(wget_commands))  # Fetch all rpm packages
    primary_node.execute('yum -y -q localinstall {}'.format(' '.join(rpm_names)))
    is_mapr_6 = mapr_version.startswith('6')
    # For MEP 4.0 onwards, MAPR_MEP_VERSION env. variable is needed by setup_mapr script.
    # And for earlier MEP versions than 4.0, the script takes no effect if that env. variable is set up.
    mapr_mep_version = ''
    if mep_version:
        mep_version_tuple = tuple(int(i) for i in mep_version.split('.'))
        if mep_version_tuple >= EARLIEST_MEP_VERSION_FOR_SETUP_MAPR_SCRIPT:
            mapr_mep_version = 'MAPR_MEP_VERSION={}'.format(mep_version[:1])
    setup_mapr_cmd = (' SDC_HOME=/opt/streamsets-datacollector SDC_CONF=/etc/sdc MAPR_HOME=/opt/mapr'
                      ' MAPR_VERSION={mapr_version} {mapr_mep_version}'
                      ' /opt/streamsets-datacollector/bin/streamsets setup-mapr >& /tmp/setup-mapr.out')
    primary_node.execute(setup_mapr_cmd.format(mapr_version=mapr_version[:5],
                                               mapr_mep_version=mapr_mep_version))
    primary_node.execute('rm -f {}'.format(' '.join(rpm_names)))
    if is_mapr_6:
        primary_node.execute('systemctl start sdc; systemctl enable sdc')
    else:
        primary_node.execute('service sdc start; chkconfig --add sdc')
