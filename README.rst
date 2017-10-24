=============================
MapR topology for clusterdock
=============================

This repository houses the **MapR** topology for `clusterdock`_.

.. _clusterdock: https://github.com/clusterdock/clusterdock

Usage
=====

Assuming you've already installed **clusterdock** (if not, go `read the docs`_),
you use this topology by cloning it to a local folder and then running commands
with the ``clusterdock`` script:

.. _read the docs: http://clusterdock.readthedocs.io/en/latest/

.. code-block:: console

    $ git clone https://github.com/clusterdock/topology_mapr.git
    $ clusterdock start topology_mapr --namespace streamsets --node-disks '{node-1:[/dev/xvdb],node-2:[/dev/xvdc]}' --predictable --mapr-version 5.2.2 --mep-version 3.0.1

To see full usage instructions for the ``start`` action, use ``-h``/``--help``:                                                 

.. code-block:: console

    $ clusterdock start topology_mapr -h
    usage: clusterdock start [--always-pull] [--namespace ns] [--network nw]
                         [-o sys] [-r url] [-h] [--mapr-version ver]
                         [--node-disks map] [--predictable]
                         [--secondary-nodes node [node ...]]
                         [--primary-node node [node ...]]
                         topology

    Start a MapR cluster
    
    positional arguments:
      topology              A clusterdock topology directory
    
    optional arguments:
      --always-pull         Pull latest images, even if they're available locally
                            (default: False)
      --namespace ns        Namespace to use when looking for images (default:
                            None)
      --network nw          Docker network to use (default: cluster)
      -o sys, --operating-system sys
                            Operating system to use for cluster nodes (default:
                            None)
      -r url, --registry url
                            Docker Registry from which to pull images (default:
                            docker.io)
      -h, --help            show this help message and exit
    
    MapR arguments:
      --mapr-version ver    MapR version to use (default: 5.2.0)
      --mep-version ver     MEP version to use (default: None)
      --node-disks map      Map of node names to block devices (default: None)
      --predictable         If specified, attempt to expose container ports to the
                            same port number on the host (default: False)
    
    Node groups:
      --secondary-nodes node [node ...]
                            Nodes of the secondary-nodes group (default:
                            ['node-2'])
      --primary-node node [node ...]
                            Nodes of the primary-node group (default: ['node-1'])
