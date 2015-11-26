import re
import fileinput
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from collections import namedtuple

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.conf import settings

from horizon import exceptions
from horizon import tables
from horizon import views

from openstack_dashboard.dashboards.logmanagement import util

from openstack_dashboard.dashboards.logmanagement.view \
    import tables as log_tables

# Regex 
OPENSTACK_TIMESTAMP = re.compile("\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\.[0-9]{6}")
OPENSTACK_PID = re.compile("\s([0-9]+)?\s")
OPENSTACK_RESOURCE = re.compile("\s([a-z\.]+)?\s")
OPENSTACK_LOGLEVEL = re.compile("([D|d]ebug|DEBUG|[N|n]otice|NOTICE|[I|i]nfo|INFO|[W|w]arn?(?:ing)?|WARN?(?:ING)?|[E|e]rr?(?:or)?|ERR?(?:OR)?|[C|c]rit?(?:ical)?|CRIT?(?:ICAL)?|[F|f]atal|FATAL|[S|s]evere|SEVERE|[A|a]udit|AUDIT)")


class IndexView(tables.DataTableView):
    template_name = 'logmanagement/view/index.html'
    page_title = _("Log Viewer")
    table_class = log_tables.LogTable

    def has_more_data(self, table):
        return self._more

    def get_project_name_from_log_file(self, filename):
        filename = filename.replace('.log', '')

        resource_map = {
            'n-': 'NOVA',
            'q-': 'NEUTRON.',
            'g-': 'GLANCE',
            'c-': 'CINDER',
            'ke': 'KEYSTONE'
        }

        for item in resource_map:
            if item == filename[0:2]:
                return resource_map[item]

        return filename

    def get_resource_name(self, filename):
        filename = filename.replace('.log', '')

        filename = filename.replace('key', 'keystone')

        resource_map = {
            'n-': 'nova.',
            'q-': 'neutron.',
            'g-': 'glance.',
            'c-': 'cinder.'
        }

        for item in resource_map:
            filename = filename.replace(item, resource_map[item])

        return filename

    # NOTE: Screen ubuntu create log file with color hex code. 
    # This function will replace these charactor from log content.
    def replace_coloredlog_format(self, text):
        color = ['\033[95m', '\033[94m', '\033[92m', '\033[93m', '\033[91m', '\033[90m', '\033[0m', '\033[32m', '\033[1m', '\033[4m']
        for c in color:
            text = text.replace(c, '')

        if not text:
            return ''
        return str(text)


    def get_date(self, datestring):
        return datestring[:10]

    def render_pandas_chart(self):
        log_path = '/opt/stack/logs/'
        file_path = log_path + 'key.log'

        if os.path.isfile(file_path):
            with open(file_path) as f:
                data = f.read()

            data_line = data.split('\n')
            data_arr = []

            for i in range(len(data_line)):
                _timestamp = re.findall(OPENSTACK_TIMESTAMP, data_line[i])
                _level = re.findall(OPENSTACK_LOGLEVEL, data_line[i])

                if not _timestamp or not _level:
                    continue
                else:
                    data_arr.append({'date': self.get_date(_timestamp[0]), 'level': _level[0], 'count': 1})
            data_frame = pd.DataFrame(data=data_arr)

            ## Render stat chart
            data_frame = pd.DataFrame(data=data_arr)
            data_frame_group = data_frame.groupby(['date','level']).agg(np.sum)
            data_frame_plot = data_frame_group.unstack().plot(
                kind='bar',
                stacked=True,
                #layout=("Date", "Number"), 
                figsize=(10, 5)
            )
            data_frame_plot.legend(loc=1, borderaxespad=0.)
            fig = data_frame_plot.get_figure()

            # NOTE: Generate chart to images
            fig.savefig(getattr(settings, 'ROOT_PATH') + "/static/dashboard/logmanagement/horizon-logmanagement-stat.png")



    def parse_log_from_file(self, filename, log_path = '/var/stack/logs/'):
        LogRow = namedtuple('logrow', 'timestamp date message project resource pid id level')
        data_arr = []
        file_path = log_path + '/' + filename
        if os.path.isfile(file_path):
            with open(file_path) as f:
                log_data = f.read()
                data_line = log_data.split('\n')

                for i in range(min(10, len(data_line))):
                    current_line = self.replace_coloredlog_format(data_line[i])

                    _level = re.findall(OPENSTACK_LOGLEVEL, current_line)
                    _pid = re.findall(OPENSTACK_PID, current_line)
                    _timestamp = re.findall(OPENSTACK_TIMESTAMP, current_line)
                    _resource = re.findall(OPENSTACK_RESOURCE, current_line)
                    
                    _message = current_line

                    if not _timestamp:
                        # Skip if not in log line
                        continue
                    else:
                        _message = _message.replace(_timestamp[0], '')

                    if not _level:
                        _level.append(None)
                    else:
                        _message = _message.replace(_level[0], '')

                    if not _resource:
                        _resource.append(None)
                    else:
                        _message = _message.replace(_resource[0], '')
                    
                    if not _pid:
                        _pid.append(None)
                    else:
                        _message = _message.replace(_pid[0], '')
                    
                    _message = _message.strip()

                    current_dict = LogRow(
                        id = data_line[i][0:10], 
                        pid = _pid[0], 
                        timestamp = _timestamp[0], 
                        date = self.get_date(_timestamp[0]),
                        level = _level[0], 
                        message = _message, 
                        resource = _resource[0],
                        project = self.get_project_name_from_log_file(filename))
                    data_arr.append(current_dict)
        
        return data_arr

    def get_data(self):
        data_arr = []
        self._more = False

        util.setConfig('x', 'y')

        log_path = '/opt/stack/logs'
        for filename in os.listdir(log_path):
            if filename.endswith(".log"):
                data_arr += self.parse_log_from_file(filename, log_path)

        # Render pandas chart
        self.render_pandas_chart()

        return data_arr