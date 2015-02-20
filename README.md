Docker Rabbitmq
===============

Usefult image for rabbitmq containers.


Environment variables
+++++++++++++++++++++

    VOLUMES:
      /data/log
      /data/mnesia
    ENV:
      RABBITMQ_NODES="rabbitmq@node1/ram,rabbitmq@node2"
      RABBITMQ_COOKIE="123131313131231231231"

