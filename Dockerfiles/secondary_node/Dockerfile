FROM cloudera/clusterdock:centos6.6_nodebase

ADD mapr_core.repo /etc/yum.repos.d/
ADD mapr_ecosystem.repo /etc/yum.repos.d/

RUN rpm --import http://package.mapr.com/releases/pub/maprgpg.key

RUN yum -y install java-1.8.0-openjdk-devel \
    mapr-core \
    mapr-fileserver \
    mapr-hbase-regionserver \
    mapr-nodemanager

# RUN chkconfig mapr-warden off
