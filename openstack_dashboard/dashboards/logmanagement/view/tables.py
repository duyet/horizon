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

class DeleteLog(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Log",
            u"Delete Logs",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Log",
            u"Deleted Logs",
            count
        )

    def delete(self, request, obj_id):
        pass


class LogTable(tables.DataTable):
    timestamp =  tables.Column("timestamp", verbose_name=_("timestamp"))
    project =  tables.Column("project", verbose_name=_("project"))
    level =  tables.Column("level", verbose_name=_("level"))
    resource =  tables.Column("resource", verbose_name=_("resource"))
    message =  tables.Column("message", verbose_name=_("message"))

    class Meta(object):
        name = "LogTable"
        verbose_name = _("LogTable")
        ajax = True

        table_actions = (DeleteLog, )