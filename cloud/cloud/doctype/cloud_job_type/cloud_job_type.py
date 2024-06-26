# Copyright (c) 2022, Frappe and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CloudJobType(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from cloud.cloud.doctype.cloud_job_type_step.cloud_job_type_step import (
			CloudJobTypeStep,
		)

		steps: DF.Table[CloudJobTypeStep]
	# end: auto-generated types

	pass
