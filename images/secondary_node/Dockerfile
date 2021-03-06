#!/bin/bash
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
ARG CENTOS_VERSION=6.6
FROM clusterdock/topology_nodebase:centos${CENTOS_VERSION}

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
    mapr-core \
    mapr-fileserver \
    mapr-hbase-regionserver \
    mapr-kafka \
    mapr-nodemanager \
    mapr-spark

# MapR script /opt/mapr/initscripts/mapr-warden sends core dump to a directory created by output of
# $(cat /proc/sys/kernel/core_pattern). On a host with Ubuntu, the command produces output like
# 'No such file or directory'. The script still proceeds without checking the correctness of previous
# command output and subsequently fails.
# To avoid this failure, the script is modified to send core dump to '/tmp' directory.
RUN sed -i 's|coresDir=$(dirname $(cat /proc/sys/kernel/core_pattern))|coresDir=/tmp|' \
    /opt/mapr/initscripts/mapr-warden

RUN useradd mapr \
    && echo mapr | passwd mapr --stdin \
    && cp -R /root/.ssh ~mapr \
    && chown -R mapr:mapr ~mapr/.ssh \
    && chkconfig mapr-warden off
