# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from django.core.exceptions import ValidationError  # noqa
from django.core.urlresolvers import reverse
from django.template import defaultfilters as filters
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from openstack_auth import utils as auth_utils

from horizon import exceptions
from horizon import forms
from horizon import tables
from keystoneclient.exceptions import Conflict  # noqa

from openstack_dashboard import api
from openstack_dashboard import policy


class LogTable(tables.DataTable):
    timestamp =  tables.Column("timestamp", verbose_name=_("timestamp"))
    pid =  tables.Column("pid", verbose_name=_("pid"))
    level =  tables.Column("level", verbose_name=_("level"))
    component =  tables.Column("component", verbose_name=_("component"))
    message =  tables.Column("message", verbose_name=_("message"))

    class Meta(object):
        name = "LogTable"
        verbose_name = _("LogTable")