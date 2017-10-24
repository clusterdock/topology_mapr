#!/bin/sh
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

# This script helps to insert correct repo URLs for the MapR.

MAPR_VERSION="$1"
MEP_VERSION="$2"

echo "baseurl = http://package.mapr.com/releases/v${MAPR_VERSION}/redhat/" >> /etc/yum.repos.d/mapr_core.repo
if [ "${MAPR_VERSION}" = "5.2.0" ] && [ -z "${MEP_VERSION}" ]; then
   echo "baseurl = http://package.mapr.com/releases/ecosystem-5.x/redhat" >> /etc/yum.repos.d/mapr_mep_ecosystem.repo
else
   echo "baseurl = http://package.mapr.com/releases/MEP/MEP-${MEP_VERSION}/redhat/" >> /etc/yum.repos.d/mapr_mep_ecosystem.repo
fi

