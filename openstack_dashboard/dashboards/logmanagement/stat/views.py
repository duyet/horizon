# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import time
import re
from collections import namedtuple

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.conf import settings

from horizon import exceptions
from horizon import messages
from horizon import tables
from horizon import views
from horizon.utils import memoized
from horizon import workflows

from openstack_dashboard import api
from openstack_dashboard.api import keystone
from openstack_dashboard import policy
from openstack_dashboard import usage
from openstack_dashboard.usage import quotas

class IndexView(views.HorizonTemplateView):
    template_name = 'logmanagement/stat/index.html'
    page_title = _("Log Stat")

    def get_data(self):
        # tenants = []
        # marker = self.request.GET.get(
        #     log_tables.LogTable._meta.pagination_param, None)
        # domain_context = self.request.session.get('domain_context', None)
        # self._more = False
        # if policy.check((("identity", "identity:list_projects"),),
        #                 self.request):
        #     try:
        #         tenants, self._more = api.keystone.tenant_list(
        #             self.request,
        #             domain=domain_context,
        #             paginate=True,
        #             marker=marker)
        #     except Exception:
        #         exceptions.handle(self.request,
        #                           _("Unable to retrieve project list."))
        # elif policy.check((("identity", "identity:list_user_projects"),),
        #                   self.request):
        #     try:
        #         tenants, self._more = api.keystone.tenant_list(
        #             self.request,
        #             user=self.request.user.id,
        #             paginate=True,
        #             marker=marker,
        #             admin=False)
        #     except Exception:
        #         exceptions.handle(self.request,
        #                           _("Unable to retrieve project information."))
        # else:
        #     msg = \
        #         _("Insufficient privilege level to view project information.")
        #     messages.info(self.request, msg)
        # return tenants
           
        tenants = []
        self._more = False

        Datum = namedtuple('datum', 'timestamp message component pid id level')

        log_path = '/var/log/apache2/'
        with open(log_path + 'keystone.log') as f:
            log_data = f.read()

        data_line = log_data.split('\n')
        data_arr = []

        OPENSTACK_TIMESTAMP = re.compile("\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\.[0-9]{6}")
        #OPENSTACK_PROG = re.compile("(?:[ a-zA-Z0-9_\-]+\.)+[ A-Za-z0-9_\-$]+")
        #OPENSTACK_PROG_SINGLE = re.compile("[A-Za-z0-9_\-$]+")
        #OPENSTACK_SOURCE = "%{OPENSTACK_PROG}|%{OPENSTACK_PROG_SINGLE}"
        #OPENSTACK_REQ_LIST = "(\[(?:(req-%{UUID}|%{UUID}|%{BASE16NUM}|None|-|%{SPACE}))+\])?"
        OPENSTACK_PID = re.compile("\s([0-9]+)?\s")
        OPENSTACK_LOGLEVEL = re.compile("([D|d]ebug|DEBUG|[N|n]otice|NOTICE|[I|i]nfo|INFO|[W|w]arn?(?:ing)?|WARN?(?:ING)?|[E|e]rr?(?:or)?|ERR?(?:OR)?|[C|c]rit?(?:ical)?|CRIT?(?:ICAL)?|[F|f]atal|FATAL|[S|s]evere|SEVERE|[A|a]udit|AUDIT)")
        #OPENSTACK_TRACE = "%{TIMESTAMP_ISO8601:timestamp} %{POSINT:pid:int} ([T|t]race|TRACE) %{OPENSTACK_SOURCE:program}%{GREEDYDATA:msg}|%{RAW_TRACE:msg}"
        #OPENSTACK_MESSAGE = "%{OPENSTACK_NORMAL}|%{OPENSTACK_TRACE}"
        #OPENSTACK_SYSLOGLINE = "%{SYSLOG5424PRINUM}%{CISCOTIMESTAMP:syslog_ts} %{HOSTNAME:syslog5424_host} %{OPENSTACK_MESSAGE:os_message}"

        for i in range(min(10000, len(data_line))):
            _level = re.findall(OPENSTACK_LOGLEVEL, data_line[i])
            _pid = re.findall(OPENSTACK_PID, data_line[i])
            _timestamp = re.findall(OPENSTACK_TIMESTAMP, data_line[i])
            
            _message = data_line[i]

            if not _level:
                _level.append(None)
            else:
                _message = _message.replace(_level[0], '')
            
            if not _pid:
                _pid.append(None)
            else:
                _message = _message.replace(_pid[0], '')
            
            if not _timestamp:
                _timestamp.append(None)
            else:
                _message = _message.replace(_timestamp[0], '')
            
            _message = _message.strip()
            

            current_dict = Datum(
                id = data_line[i][0:10], 
                pid = _pid[0], 
                timestamp = _timestamp[0], 
                level = _level[0], 
                message = _message, 
                component = 1)
            data_arr.append(current_dict)
        

        return data_arr