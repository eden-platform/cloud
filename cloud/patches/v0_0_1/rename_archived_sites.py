# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and Contributors
# For license information, please see license.txt


import frappe
from cloud.cloud.doctype.site.site import release_name


def execute():
	frappe.reload_doc("cloud", "doctype", "site")
	sites = frappe.get_all("Site", filters={"status": "Archived"})
	for site in sites:
		release_name(site.name)
		frappe.db.commit()
