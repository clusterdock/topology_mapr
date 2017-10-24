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

FROM clusterdock/topology_nodebase:centos6.6

# Build arguments.
ARG MAPR_VERSION
ARG MEP_VERSION
ARG REPO_URL_INSERT_SCRIPT=repo_url_insert_script.sh

ADD mapr_core.repo /etc/yum.repos.d/
ADD mapr_mep_ecosystem.repo /etc/yum.repos.d/
ADD ${REPO_URL_INSERT_SCRIPT} /tmp

RUN . /tmp/${REPO_URL_INSERT_SCRIPT} ${MAPR_VERSION} ${MEP_VERSION}

RUN rpm --import http://package.mapr.com/releases/pub/maprgpg.key

RUN yum -y install java-1.8.0-openjdk-devel \
    mapr-cldb \
    mapr-core \
    mapr-fileserver \
    mapr-gateway \
    mapr-hbase \
    mapr-hbasethrift \
    mapr-hbase-master \
    mapr-hbase-regionserver \
    mapr-hbase-rest \
    mapr-historyserver \
    mapr-hive \
    mapr-hiveserver2 \
    mapr-httpfs \
    mapr-kafka \
    mapr-nodemanager \
    mapr-resourcemanager \
    mapr-spark \
    mapr-webserver \
    mapr-zookeeper \
    mysql-server
