# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe and Contributors
# See license.txt


import typing
import frappe
import unittest

from press.press.doctype.ssh_key.test_ssh_key import create_test_ssh_key
from press.press.doctype.virtual_machine_image.virtual_machine_image import (
	VirtualMachineImage,
)

if typing.TYPE_CHECKING:
	from press.press.doctype.cluster.cluster import Cluster

from unittest.mock import MagicMock, patch


@patch("press.press.doctype.cluster.cluster.boto3.client", new=MagicMock())
def create_test_cluster(
	name: str = "Mumbai", region: str = "ap-south-1", public: bool = False
) -> "Cluster":
	"""Create test Cluster doc"""
	doc = frappe.get_doc(
		{
			"doctype": "Cluster",
			"name": name,
			"region": region,
			"availability_zone": "ap-south-1a",
			"cloud_provider": "AWS EC2",
			"ssh_key": create_test_ssh_key().name,
			"subnet_cidr_block": "10.3.0.0/16",
			"aws_access_key_id": "test",
			"aws_secret_access_key": "test",
			"public": public,
		}
	).insert(ignore_if_duplicate=True)
	doc.reload()
	return doc


def successful_sync(self: VirtualMachineImage):
	self.aws_instance_id = "ami-1234567890"
	self.status = "Available"
	self.save()


class TestCluster(unittest.TestCase):
	def tearDown(self) -> None:
		frappe.db.rollback()

	@patch.object(VirtualMachineImage, "create_image", new=successful_sync)
	@patch.object(VirtualMachineImage, "create_image_from_copy", new=successful_sync)
	def test_creation_cluster_in_new_region_copies_VMIs_from_other_region(self):
		from press.press.doctype.virtual_machine_image.test_virtual_machine_image import (
			create_test_virtual_machine_image,
		)

		cluster = create_test_cluster(name="Mumbai", region="ap-south-1")
		create_test_virtual_machine_image(cluster=cluster, series="m")
		create_test_virtual_machine_image(cluster=cluster, series="f")
		vmi_count_before = frappe.db.count("Virtual Machine Image")
		create_test_cluster(name="Frankfurt", region="eu-central-1")
		vmi_count_after = frappe.db.count("Virtual Machine Image")
		self.assertEqual(vmi_count_before, 2)
		self.assertEqual(vmi_count_after, vmi_count_before * 2)

	@patch.object(VirtualMachineImage, "create_image", new=successful_sync)
	@patch.object(VirtualMachineImage, "create_image_from_copy", new=successful_sync)
	def test_creation_of_cluster_in_same_region_reuses_VMIs(self):
		from press.press.doctype.virtual_machine_image.test_virtual_machine_image import (
			create_test_virtual_machine_image,
		)

		cluster = create_test_cluster(name="Mumbai", region="ap-south-1")
		create_test_virtual_machine_image(cluster=cluster, series="m")
		create_test_virtual_machine_image(cluster=cluster, series="f")
		vmi_count_before = frappe.db.count("Virtual Machine Image")
		create_test_cluster(name="Mumbai 2", region="ap-south-1")
		vmi_count_after = frappe.db.count("Virtual Machine Image")
		self.assertEqual(vmi_count_before, 2)
		self.assertEqual(vmi_count_after, vmi_count_before)

	@patch.object(VirtualMachineImage, "create_image", new=successful_sync)
	@patch.object(VirtualMachineImage, "create_image_from_copy", new=successful_sync)
	def test_creation_of_public_cluster_only_adds_3_vms(self):
		from press.press.doctype.virtual_machine_image.test_virtual_machine_image import (
			create_test_virtual_machine_image,
		)

		cluster = create_test_cluster(name="Mumbai", region="ap-south-1", public=True)
		create_test_virtual_machine_image(cluster=cluster, series="m")
		create_test_virtual_machine_image(cluster=cluster, series="f")
		create_test_virtual_machine_image(cluster=cluster, series="n")
		create_test_virtual_machine_image(cluster=cluster, series="p")
		create_test_virtual_machine_image(cluster=cluster, series="e")
		vm_count_before = frappe.db.count("Virtual Machine Image")
		create_test_cluster(name="Frankfurt", region="eu-central-1", public=True)
		vm_count_after = frappe.db.count("Virtual Machine Image")
		self.assertEqual(vm_count_before, 5)
		self.assertEqual(vm_count_after, vm_count_before + 3)
