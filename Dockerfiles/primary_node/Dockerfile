FROM clusterdock/topology_nodebase:centos6.6

ADD mapr_core.repo /etc/yum.repos.d/
ADD mapr_ecosystem.repo /etc/yum.repos.d/

RUN rpm --import http://package.mapr.com/releases/pub/maprgpg.key

RUN yum -y install java-1.8.0-openjdk-devel \
    mapr-cldb \
    mapr-core \
    mapr-drill \
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

# Even with owner mapr, Docker has issues writing files into zkdata as the mapr user.
# https://forums.docker.com/t/permission-erros-to-create-subdirectories/17771 suggested
# this workaround, which seems to work for us.
VOLUME /opt/mapr/zkdata

RUN useradd mapr \
    && echo mapr | passwd mapr --stdin \
    && cp -R /root/.ssh ~mapr \
    && chown -R mapr:mapr ~mapr/.ssh \
    && chown -R mapr:mapr /opt/mapr/httpfs \
    && chkconfig mapr-warden off \
    && chkconfig mapr-zookeeper off

RUN groupadd -r -g 20159 sdc \
    && useradd -r -g sdc -u 20159 sdc
