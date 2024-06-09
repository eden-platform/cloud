# Copyright (c) 2024, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from cloud.api.client import dashboard_whitelist


class CloudRole(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from cloud.cloud.doctype.cloud_role_user.cloud_role_user import CloudRoleUser

		allow_apps: DF.Check
		allow_bench_creation: DF.Check
		allow_billing: DF.Check
		allow_server_creation: DF.Check
		allow_site_creation: DF.Check
		team: DF.Link
		title: DF.Data
		users: DF.Table[CloudRoleUser]
	# end: auto-generated types

	dashboard_fields = [
		"title",
		"users",
		"allow_billing",
		"allow_apps",
		"allow_site_creation",
		"allow_bench_creation",
		"allow_server_creation",
		"team",
	]

	def before_insert(self):
		if frappe.db.exists("Cloud Role", {"title": self.title, "team": self.team}):
			frappe.throw(
				"Role with title {0} already exists".format(self.title), frappe.DuplicateEntryError
			)

		if not frappe.local.system_user() and frappe.session.user != frappe.db.get_value(
			"Team", self.team, "user"
		):
			frappe.throw("Only the team owner can create roles")

	@dashboard_whitelist()
	def add_user(self, user):
		user_exists = self.get("users", {"user": user})
		if user_exists:
			frappe.throw(f"{user} already belongs to {self.title}")

		self.append("users", {"user": user})
		self.save()

	@dashboard_whitelist()
	def remove_user(self, user):
		user_exists = self.get("users", {"user": user})
		if not user_exists:
			frappe.throw(f"{user} does not belong to {self.title}")

		for row in self.users:
			if row.user == user:
				self.remove(row)
				break
		self.save()

	@dashboard_whitelist()
	def delete_permissions(self, permissions: list[str]) -> None:
		for perm in permissions:
			perm_doc = frappe.get_doc("Cloud Role Permission", perm)
			if perm_doc.role == self.name:
				perm_doc.delete()

	@dashboard_whitelist()
	def delete(self):
		if not frappe.local.system_user() and frappe.session.user != frappe.db.get_value(
			"Team", self.team, "user"
		):
			frappe.throw("Only the team owner can delete this role")

		super().delete()

	def on_trash(self):
		frappe.db.delete("Cloud Role Permission", {"role": self.name})


def check_role_permissions(doctype: str, name: str | None = None) -> list[str] | None:
	"""
	Check if the user is permitted to access the document based on the role permissions
	Expects the function to throw error for `get` if no permission and return a list of permitted roles for `get_list`
	Note: Empty list means no restrictions

	:param doctype: Document type
	:param name: Document name
	:return: List of permitted roles or None
	"""
	if doctype not in ["Site", "Release Group", "Server", "Marketplace App"]:
		return []

	if frappe.local.system_user():
		return []

	CloudRoleUser = frappe.qb.DocType("Cloud Role User")
	CloudRole = frappe.qb.DocType("Cloud Role")

	query = (
		frappe.qb.from_(CloudRole)
		.select(CloudRole.name)
		.join(CloudRoleUser)
		.on(CloudRoleUser.parent == CloudRole.name)
		.where(CloudRoleUser.user == frappe.session.user)
		.where(CloudRole.team == frappe.local.team().name)
	)

	if doctype == "Marketplace App":
		if roles := query.select(CloudRole.allow_apps).run(as_dict=1):
			# throw error if any of the roles don't have permission for apps
			if not any(perm.allow_apps for perm in roles):
				frappe.throw("Not permitted", frappe.PermissionError)

	elif doctype in ["Site", "Release Group", "Server"]:
		field = doctype.lower().replace(" ", "_")
		if roles := query.run(as_dict=1, pluck="name"):
			perms = frappe.db.get_all(
				"Cloud Role Permission",
				filters={"role": ["in", roles], field: name},
			)
			if not perms and name:
				# throw error if the user is not permitted for the document
				frappe.throw("Not permitted", frappe.PermissionError)
			else:
				return roles

	return []


def add_permission_for_newly_created_doc(doc: Document) -> None:
	"""
	Used to bulk insert permissions right after a site/release group/server is created
	for users with create permission for respective doctype is enabled
	"""

	doctype = doc.doctype
	if doctype not in ["Site", "Release Group", "Server"]:
		return

	role_fieldname = ""
	fieldname = doctype.lower().replace(" ", "_")
	if doctype == "Site":
		role_fieldname = "allow_site_creation"
	elif doctype == "Server":
		role_fieldname = "allow_server_creation"
	elif doctype == "Release Group":
		role_fieldname = "allow_bench_creation"

	new_perms = []
	CloudRole = frappe.qb.DocType("Cloud Role")
	CloudRoleUser = frappe.qb.DocType("Cloud Role User")
	if roles := (
		frappe.qb.from_(CloudRole)
		.select(CloudRole.name)
		.join(CloudRoleUser)
		.on(CloudRoleUser.parent == CloudRole.name)
		.where(CloudRoleUser.user == frappe.session.user)
		.where(CloudRole.team == doc.team)
		.where(CloudRole[role_fieldname] == 1)
		.run(as_dict=1, pluck="name")
	):
		for role in roles:
			new_perms.append(
				(
					frappe.generate_hash(length=12),
					role,
					doc.name,
					doc.team,
					frappe.utils.now(),
					frappe.utils.now(),
				)
			)

	if new_perms:
		frappe.db.bulk_insert(
			"Cloud Role Permission",
			fields=["name", "role", fieldname, "team", "creation", "modified"],
			values=set(new_perms),
		)
