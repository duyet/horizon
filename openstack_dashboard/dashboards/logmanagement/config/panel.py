from django.utils.translation import ugettext_lazy as _

import horizon

from openstack_dashboard.dashboards.logmanagement import dashboard

class LogManagerConfig(horizon.Panel):
    name = _("Config")
    slug = 'config'

dashboard.Logmanagement.register(LogManagerConfig)
