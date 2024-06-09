import frappe


def execute():
	frappe.db.sql(
		"update `tabSite Backup` set files_availability = 'Available' where `site` not"
		" like '%edencloud.us.archived%'"
	)
	frappe.db.sql(
		"update `tabSite Backup` set files_availability = 'Unavailable' where `site`"
		" like '%edencloud.us.archived%'"
	)
	frappe.db.commit()
