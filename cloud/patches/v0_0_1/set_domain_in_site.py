# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and Contributors
# For license information, please see license.txt


import frappe


def execute():
	frappe.reload_doc("cloud", "doctype", "site")
	domain = frappe.db.get_single_value("Cloud Settings", "domain")
	frappe.db.sql(
		"UPDATE tabSite SET domain = %s WHERE IFNULL(domain, '') = ''", (domain,)
	)
