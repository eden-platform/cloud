import frappe
from cloud.cloud.doctype.server.server import get_hostname_abbreviation


def execute():
	for doctype in ["Server", "Database Server", "Proxy Server"]:
		frappe.reload_doc("cloud", "doctype", doctype)

		for doc in frappe.get_all(doctype, fields=["name", "hostname"]):
			abbr = get_hostname_abbreviation(doc.hostname)

			frappe.db.set_value(
				doctype, doc.name, "hostname_abbreviation", abbr, update_modified=False
			)
