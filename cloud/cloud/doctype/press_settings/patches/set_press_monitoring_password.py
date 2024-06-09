import frappe


def execute():
	frappe.reload_doctype("Cloud Settings")
	settings = frappe.get_single("Cloud Settings")
	try:
		settings.get_password("cloud_monitoring_password")
	except frappe.AuthenticationError:
		settings.cloud_monitoring_password = frappe.generate_hash()
		settings.save()
