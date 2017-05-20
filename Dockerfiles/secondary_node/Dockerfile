FROM clusterdock/topology_nodebase:centos6.6

ADD mapr_core.repo /etc/yum.repos.d/
ADD mapr_ecosystem.repo /etc/yum.repos.d/

RUN rpm --import http://package.mapr.com/releases/pub/maprgpg.key

RUN yum -y install java-1.8.0-openjdk-devel \
    mapr-core \
    mapr-fileserver \
    mapr-hbase-regionserver \
    mapr-nodemanager

RUN groupadd -r -g 20159 sdc \
    && useradd -r -g sdc -u 20159 sdc
