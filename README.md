<!---
  Licensed to the Apache Software Foundation (ASF) under one
  or more contributor license agreements.  See the NOTICE file
  distributed with this work for additional information
  regarding copyright ownership.  The ASF licenses this file
  to you under the Apache License, Version 2.0 (the
  "License"); you may not use this file except in compliance
  with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing,
  software distributed under the License is distributed on an
  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
  KIND, either express or implied.  See the License for the
  specific language governing permissions and limitations
  under the License.
-->
# MapR Converged Data Platform clusterdock topology

## Overview
This topology can be used to build and start clusters of the MapR Converged Data Platform.

## Usage
The *clusterdock* framework is designed to be run out of its own container while affecting
operations on the host. To avoid problems that might result from incorrectly
formatting this framework invocation, a Bash helper script (`clusterdock.sh`) can be sourced on a
host that has Docker installed. Afterwards, running any of the binaries intended to carry
out *clusterdock* actions can be done using the `clusterdock_run` command.
```
wget https://raw.githubusercontent.com/clusterdock/framework/master/clusterdock.sh
# ALWAYS INSPECT SCRIPTS FROM THE INTERNET BEFORE SOURCING THEM.
source clusterdock.sh
```

An environmental variable is used to let the helper script know where to find an image of the *mapr*
topology. Note that each MapR cluster node requires a dedicated disk or partition. This is passed 
when starting the cluster with the `--node-disks` argument. To start a two-node MapR Converged Data 
Platform cluster with default versions, you would simply run
```
CLUSTERDOCK_TOPOLOGY_IMAGE=clusterdock/topology_mapr clusterdock_run \
    ./bin/start_cluster mapr --node-disks='{node-1:[/dev/xvdb],node-2:[/dev/xvdc]}' 
```
