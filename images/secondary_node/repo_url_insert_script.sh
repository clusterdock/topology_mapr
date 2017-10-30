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

set_repos() {
    echo "baseurl = http://package.mapr.com/releases/v${MAPR_VERSION}/redhat/" >> /etc/yum.repos.d/mapr_core.repo
    echo "baseurl = http://package.mapr.com/releases/MEP/MEP-${MEP_VERSION}/redhat/" >> /etc/yum.repos.d/mapr_mep_ecosystem.repo
}

case "${MAPR_VERSION}" in
    "5.2.0")
        echo "Inside ${MAPR_VERSION}"
        if [ -z "${MEP_VERSION}" ]; then
            echo "Inside 5.2.0 Ecosystem"
            echo "baseurl = http://package.mapr.com/releases/v${MAPR_VERSION}/redhat/" >> /etc/yum.repos.d/mapr_core.repo
            echo "baseurl = http://package.mapr.com/releases/ecosystem-5.x/redhat" >> /etc/yum.repos.d/mapr_mep_ecosystem.repo
        else
            set_repos
        fi
        ;;
    "6.0.0-RC1")
        echo "Inside ${MAPR_VERSION}"
        echo "baseurl = http://package.mapr.com/v6.0.0-rc1/v6.0.0/redhat/" >> /etc/yum.repos.d/mapr_core.repo
        echo "baseurl = http://package.mapr.com/v6.0.0-rc1/MEP/MEP-${MEP_VERSION}/redhat/" >> /etc/yum.repos.d/mapr_mep_ecosystem.repo
        ;;
    *)
        set_repos
        ;;
esac
