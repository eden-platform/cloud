# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe and contributors
# For license information, please see license.txt


import frappe


def execute():
	frappe.reload_doc("cloud", "doctype", "root_domain")
	cloud_settings = frappe.get_doc("Cloud Settings", "Cloud Settings")
	if (
		cloud_settings.domain
		and cloud_settings.aws_secret_access_key
		and not frappe.db.exists("Root Domain", cloud_settings.domain)
	):
		default_cluster = frappe.db.get_value("Cluster", {"default": True})
		frappe.get_doc(
			{
				"doctype": "Root Domain",
				"name": cloud_settings.domain,
				"default_cluster": default_cluster,
				"dns_provider": cloud_settings.dns_provider,
				"aws_access_key_id": cloud_settings.aws_access_key_id,
				"aws_secret_access_key": cloud_settings.get_password("aws_secret_access_key"),
			}
		).insert()
