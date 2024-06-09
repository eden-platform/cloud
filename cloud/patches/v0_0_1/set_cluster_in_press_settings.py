# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe and contributors
# For license information, please see license.txt


import frappe


def execute():
	frappe.reload_doc("cloud", "doctype", "erpnext_app")
	frappe.reload_doc("cloud", "doctype", "cloud_settings")
	frappe.clear_cache()
	cloud_settings = frappe.get_doc("Cloud Settings", "Cloud Settings")
	if not cloud_settings.get("cluster"):
		cloud_settings.cluster = frappe.db.get_value(
			"Root Domain", cloud_settings.domain, "default_cluster"
		)
		cloud_settings.save()
