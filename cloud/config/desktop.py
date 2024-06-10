# -*- coding: utf-8 -*-

from frappe import _


def get_data():
	return [
		{
			"module_name": "Cloud",
			"category": "Modules",
			"color": "grey",
			"description": "Cloud Management System for the Eden Platform",
			"icon": "octicon octicon-rocket",
			"type": "module",
			"label": _("Cloud"),
			"reverse": 1,
		}
	]
