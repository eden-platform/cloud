from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import frappe
from frappe.tests.utils import FrappeTestCase

from cloud.cloud.audit import BackupRecordCheck, OffsiteBackupCheck
from cloud.cloud.doctype.agent_job.agent_job import AgentJob
from cloud.cloud.doctype.cloud_settings.test_cloud_settings import (
	create_test_cloud_settings,
)
from cloud.cloud.doctype.site.test_site import create_test_site
from cloud.cloud.doctype.site_backup.test_site_backup import create_test_site_backup
from cloud.telegram_utils import Telegram


@patch.object(Telegram, "send", new=Mock())
@patch.object(AgentJob, "enqueue_http_request", new=Mock())
class TestBackupRecordCheck(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	older_than_interval = datetime.now() - timedelta(
		hours=(BackupRecordCheck.interval + 2)
	)

	def test_audit_will_fail_if_backup_older_than_interval(self):
		create_test_cloud_settings()
		site = create_test_site(creation=self.older_than_interval)
		create_test_site_backup(
			site.name, creation=datetime.now() - timedelta(hours=BackupRecordCheck.interval + 1)
		)
		BackupRecordCheck()
		audit_log = frappe.get_last_doc(
			"Audit Log", {"audit_type": BackupRecordCheck.audit_type}
		)
		self.assertEqual(audit_log.status, "Failure")

	def test_audit_succeeds_when_backup_in_interval_exists(self):
		create_test_cloud_settings()
		site = create_test_site(creation=self.older_than_interval)

		create_test_site_backup(
			site.name,
			creation=frappe.utils.now_datetime()
			- timedelta(hours=BackupRecordCheck.interval - 1),
		)
		BackupRecordCheck()
		audit_log = frappe.get_last_doc(
			"Audit Log", {"audit_type": BackupRecordCheck.audit_type}
		)
		self.assertEqual(audit_log.status, "Success")

	def test_audit_log_is_created(self):
		create_test_cloud_settings()
		site = create_test_site(creation=self.older_than_interval)
		create_test_site_backup(
			site.name, creation=datetime.now() - timedelta(hours=BackupRecordCheck.interval + 0)
		)
		audit_logs_before = frappe.db.count(
			"Audit Log", {"audit_type": BackupRecordCheck.audit_type}
		)
		BackupRecordCheck()
		audit_logs_after = frappe.db.count(
			"Audit Log", {"audit_type": BackupRecordCheck.audit_type}
		)
		self.assertGreater(audit_logs_after, audit_logs_before)

	def test_sites_created_within_interval_are_ignored(self):
		create_test_cloud_settings()
		create_test_site()
		# no backup
		BackupRecordCheck()

		audit_log = frappe.get_last_doc(
			"Audit Log", {"audit_type": BackupRecordCheck.audit_type}
		)
		self.assertEqual(audit_log.status, "Success")


@patch.object(Telegram, "send", new=Mock())
@patch.object(AgentJob, "enqueue_http_request", new=Mock())
class TestOffsiteBackupCheck(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_audit_succeeds_when_all_remote_files_are_in_remote(self):
		create_test_cloud_settings()
		site = create_test_site()
		site_backup = create_test_site_backup(site.name)
		frappe.db.set_value(
			"Remote File", site_backup.remote_database_file, "file_path", "remote_file1"
		)
		frappe.db.set_value(
			"Remote File", site_backup.remote_public_file, "file_path", "remote_file2"
		)
		frappe.db.set_value(
			"Remote File", site_backup.remote_private_file, "file_path", "remote_file3"
		)
		with patch.object(
			OffsiteBackupCheck,
			"_get_all_files_in_s3",
			new=lambda x: ["remote_file1", "remote_file2", "remote_file3"],
		):
			OffsiteBackupCheck()
		audit_log = frappe.get_last_doc(
			"Audit Log", {"audit_type": OffsiteBackupCheck.audit_type}
		)
		self.assertEqual(audit_log.status, "Success")

	def test_audit_fails_when_all_remote_files_not_in_remote(self):
		create_test_cloud_settings()
		site = create_test_site()
		# 3 remote files are created here
		site_backup = create_test_site_backup(site.name)
		frappe.db.set_value(
			"Remote File", site_backup.remote_database_file, "file_path", "remote_file1"
		)
		with patch.object(
			OffsiteBackupCheck, "_get_all_files_in_s3", new=lambda x: ["remote_file1"]
		):
			OffsiteBackupCheck()
		audit_log = frappe.get_last_doc(
			"Audit Log", {"audit_type": OffsiteBackupCheck.audit_type}
		)
		self.assertEqual(audit_log.status, "Failure")
