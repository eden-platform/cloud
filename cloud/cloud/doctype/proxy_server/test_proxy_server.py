# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and Contributors
# See license.txt

import unittest
from typing import Dict, List
from unittest.mock import Mock, patch

import frappe
from frappe.model.naming import make_autoname

from cloud.cloud.doctype.cloud_settings.test_cloud_settings import (
	create_test_cloud_settings,
)
from cloud.cloud.doctype.proxy_server.proxy_server import ProxyServer
from cloud.cloud.doctype.server.server import BaseServer


@patch.object(BaseServer, "after_insert", new=Mock())
@patch.object(ProxyServer, "validate_domains", new=Mock())
def create_test_proxy_server(
	hostname: str = "n",
	domain: str = "fc.dev",
	domains: List[Dict[str, str]] = [{"domain": "fc.dev"}],
	cluster: str = "Default",
):
	"""Create test Proxy Server doc"""
	create_test_cloud_settings()
	server = frappe.get_doc(
		{
			"doctype": "Proxy Server",
			"status": "Active",
			"ip": frappe.mock("ipv4"),
			"private_ip": frappe.mock("ipv4_private"),
			"hostname": make_autoname(hostname + ".######"),
			"cluster": cluster,
			"domain": domain,
			"domains": domains,
		}
	).insert(ignore_if_duplicate=True)
	server.reload()
	return server


class TestProxyServer(unittest.TestCase):
	pass
