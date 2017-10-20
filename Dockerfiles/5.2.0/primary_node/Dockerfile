FROM clusterdock/topology_nodebase:centos6.6

ADD mapr_core.repo /etc/yum.repos.d/
ADD mapr_ecosystem.repo /etc/yum.repos.d/

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
