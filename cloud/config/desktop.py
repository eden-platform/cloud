# -*- coding: utf-8 -*-

from frappe import _


def get_data():
	return [
		{
			"module_name": "Cloud",
			"category": "Modules",
			"color": "grey",
			"description": "Managed Frappe Hosting",
			"icon": "octicon octicon-rocket",
			"type": "module",
			"label": _("Cloud"),
			"reverse": 1,
		}
	]
