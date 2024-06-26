# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document


class DeployCandidateDifferenceApp(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		app: DF.Link
		deploy_type: DF.Literal["Pull", "Migrate"]
		destination_release: DF.Link | None
		difference: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		source_release: DF.Link | None
	# end: auto-generated types

	dashboard_fields = ["difference", "app"]

def get_list_query(query):
		apps = query.run(as_dict=True)
		for app in apps:
			app["source_tag"] = frappe.db.get_value(
				"App Tag", {"hash": app["source_hash"]}, "tag"
			)
			app["destination_tag"] = frappe.db.get_value(
				"App Tag", {"hash": app["destination_hash"]}, "tag"
			)
		return apps
