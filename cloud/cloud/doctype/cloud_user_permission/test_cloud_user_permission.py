# Copyright (c) 2023, Frappe and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from cloud.cloud.doctype.cloud_user_permission.cloud_user_permission import (
	has_user_permission,
)
from cloud.cloud.doctype.site.test_site import create_test_site
from cloud.cloud.doctype.team.test_team import create_test_team


class TestCloudUserPermission(FrappeTestCase):
	def setUp(self):
		self.team = create_test_team()
		self.site = create_test_site(subdomain="testpermsite")

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback()

	def test_cloud_user_permission(self):
		self.assertFalse(has_user_permission("Site", self.site.name, "cloud.api.site.login"))

		frappe.get_doc(
			doctype="Cloud User Permission",
			type="User",
			user=frappe.session.user,
			document_type="Site",
			document_name=self.site.name,
			action="cloud.api.site.login",
		).insert(ignore_permissions=True)

		self.assertTrue(has_user_permission("Site", self.site.name, "cloud.api.site.login"))
		self.assertFalse(
			has_user_permission("Site", self.site.name, "cloud.api.site.migrate")
		)

	def test_cloud_group_permission(self):
		group = frappe.get_doc(
			doctype="Cloud Permission Group", team=self.team.name, title="Test Group"
		)
		group.append("users", {"user": frappe.session.user})
		group.insert(ignore_permissions=True)

		frappe.get_doc(
			doctype="Cloud User Permission",
			type="Group",
			group=group.name,
			document_type="Site",
			document_name=self.site.name,
			action="cloud.api.site.overview",
		).insert(ignore_permissions=True)

		self.assertTrue(
			has_user_permission(
				"Site", self.site.name, "cloud.api.site.overview", groups=[group.name]
			)
		)
		self.assertFalse(
			has_user_permission(
				"Site", self.site.name, "cloud.api.site.migrate", groups=[group.name]
			)
		)

	def test_cloud_config_permission(self):
		perms = {
			"global": {
				"Site": {"*": "cloud.api.site.login"},
			},
			"restricted": {"Site": {"test.frappe.dev": "cloud.api.site.migrate"}},
		}
		frappe.get_doc(
			doctype="Cloud User Permission",
			type="Config",
			config=frappe.as_json(perms),
			user=frappe.session.user,
		).insert(ignore_permissions=True)

		self.assertTrue(has_user_permission("Site", self.site.name, "cloud.api.site.login"))
		self.assertFalse(
			has_user_permission("Site", "sometest.frappe.dev", "cloud.api.site.restore")
		)
		self.assertFalse(
			has_user_permission("Site", "test.frappe.dev", "cloud.api.site.migrate")
		)
		self.assertTrue(
			has_user_permission("Site", "test.frappe.dev", "cloud.api.site.login")
		)
