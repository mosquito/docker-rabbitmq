FROM                centos:centos7
MAINTAINER          Dmitry Orlov <me@mosquito.su>

RUN                 mkdir -p /data
WORKDIR             /data
VOLUME              ["/data/log", "/data/mnesia"]
EXPOSE              5672 15672

# Preparing system
RUN                 yum install -y http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm
RUN                 yum install -y http://dl.iuscommunity.org/pub/ius/stable/CentOS/7/x86_64/ius-release-1.0-13.ius.centos7.noarch.rpm
RUN                 yum upgrade -y
RUN                 yum install -y http://www.rabbitmq.com/releases/rabbitmq-server/v3.4.4/rabbitmq-server-3.4.4-1.noarch.rpm

ADD                 entrypoint.py /usr/local/bin/entrypoint
RUN                 mkdir -p /etc/rabbitmq && touch /etc/rabbitmq/rabbitmq.config /etc/rabbitmq/enabled_plugins
RUN                 chown rabbitmq:rabbitmq -R /etc/rabbitmq
RUN                 rabbitmq-plugins enable --offline rabbitmq_management
ENTRYPOINT          ["/usr/local/bin/entrypoint"]