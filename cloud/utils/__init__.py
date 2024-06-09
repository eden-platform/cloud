# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt

import functools
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urljoin

import frappe
import pytz
import requests
import wrapt
from frappe.utils import get_datetime, get_system_timezone
from frappe.utils.caching import site_cache
from pymysql.err import InterfaceError


def log_error(title, **kwargs):
	if frappe.flags.in_test:
		try:
			raise
		except RuntimeError as e:
			if e.args[0] == "No active exception to reraise":
				pass
			else:
				raise

	reference_doctype = kwargs.get("reference_doctype")
	reference_name = kwargs.get("reference_name")

	# Prevent double logging as `message`
	if reference_doctype and reference_name:
		del kwargs["reference_doctype"]
		del kwargs["reference_name"]

	if doc := kwargs.get("doc"):
		reference_doctype = doc.doctype
		reference_name = doc.name
		del kwargs["doc"]

	try:
		kwargs["user"] = frappe.session.user
		kwargs["team"] = frappe.local.team()
	except Exception:
		pass

	traceback = frappe.get_traceback(with_context=True)
	serialized = json.dumps(kwargs, indent=4, sort_keys=True, default=str, skipkeys=True)
	message = f"Data:\n{serialized}\nException:\n{traceback}"

	try:
		frappe.log_error(
			title=title,
			message=message,
			reference_doctype=reference_doctype,
			reference_name=reference_name,
		)
	except Exception:
		pass


def get_current_team(get_doc=False):
	if frappe.session.user == "Guest":
		frappe.throw("Not Permitted", frappe.PermissionError)

	if not hasattr(frappe.local, "request"):
		# if this is not a request, send the current user as default team
		# always use parent_team for background jobs
		return (
			frappe.get_doc(
				"Team",
				{"user": frappe.session.user, "enabled": 1, "parent_team": ("is", "not set")},
			)
			if get_doc
			else frappe.get_value(
				"Team",
				{"user": frappe.session.user, "enabled": 1, "parent_team": ("is", "not set")},
				"name",
			)
		)

	system_user = frappe.session.data.user_type == "System User"

	# get team passed via request header
	team = frappe.get_request_header("X-Press-Team")

	user_is_press_admin = frappe.db.exists(
		"Has Role", {"parent": frappe.session.user, "role": "Press Admin"}
	)

	if (
		not team
		and user_is_press_admin
		and frappe.db.exists("Team", {"user": frappe.session.user})
	):
		# if user has_role of Press Admin then just return current user as default team
		return (
			frappe.get_doc("Team", {"user": frappe.session.user, "enabled": 1})
			if get_doc
			else frappe.get_value("Team", {"user": frappe.session.user, "enabled": 1}, "name")
		)

	if not team:
		# if team is not passed via header, get the default team for user
		team = get_default_team_for_user(frappe.session.user)

	if not system_user and not is_user_part_of_team(frappe.session.user, team):
		# if user is not part of the team, get the default team for user
		team = get_default_team_for_user(frappe.session.user)
		if not team:
			frappe.throw(
				"User {0} does not belong to Team {1}".format(frappe.session.user, team),
				frappe.PermissionError,
			)

	if not frappe.db.exists("Team", {"name": team, "enabled": 1}):
		frappe.throw("Invalid Team", frappe.PermissionError)

	if get_doc:
		return frappe.get_doc("Team", team)

	return team


def _get_current_team():
	if not getattr(frappe.local, "_current_team", None):
		frappe.local._current_team = get_current_team(get_doc=True)
	return frappe.local._current_team


def _system_user():
	return (
		frappe.get_cached_value("User", frappe.session.user, "user_type") == "System User"
	)


@functools.lru_cache(maxsize=1024)
def get_app_tag(repository, repository_owner, hash):
	return frappe.db.get_value(
		"App Tag",
		{"repository": repository, "repository_owner": repository_owner, "hash": hash},
		"tag",
	)


def get_default_team_for_user(user):
	"""Returns the Team if user has one, or returns the Team in which they belong"""
	if frappe.db.exists("Team", {"user": user, "enabled": 1}):
		return frappe.db.get_value("Team", {"user": user, "enabled": 1}, "name")

	teams = frappe.db.get_values(
		"Team Member",
		filters={"parenttype": "Team", "user": user},
		fieldname="parent",
		pluck="parent",
	)
	for team in teams:
		# if user is part of multiple teams, send the first enabled one
		if frappe.db.exists("Team", {"name": team, "enabled": 1}):
			return team


def get_valid_teams_for_user(user):
	teams = frappe.db.get_all("Team Member", filters={"user": user}, pluck="parent")
	valid_teams = frappe.db.get_all(
		"Team", filters={"name": ("in", teams), "enabled": 1}, fields=["name", "user"]
	)
	return valid_teams


def is_user_part_of_team(user, team):
	"""Returns True if user is part of the team"""
	return frappe.db.exists(
		"Team Member", {"parenttype": "Team", "parent": team, "user": user}
	)


def get_country_info():
	if frappe.flags.in_test:
		return {}

	ip = frappe.local.request_ip
	ip_api_key = frappe.conf.get("ip-api-key")

	def _get_country_info():
		fields = [
			"status",
			"message",
			"continent",
			"continentCode",
			"country",
			"countryCode",
			"region",
			"regionName",
			"city",
			"district",
			"zip",
			"lat",
			"lon",
			"timezone",
			"offset",
			"currency",
			"isp",
			"org",
			"as",
			"asname",
			"reverse",
			"mobile",
			"proxy",
			"hosting",
			"query",
		]

		res = requests.get(
			"https://pro.ip-api.com/json/{ip}?key={key}&fields={fields}".format(
				ip=ip, key=ip_api_key, fields=",".join(fields)
			)
		)
		try:
			data = res.json()
			if data.get("status") != "fail":
				return data
		except Exception:
			pass

		return {}

	return frappe.cache().hget("ip_country_map", ip, generator=_get_country_info)


def get_last_doc(*args, **kwargs):
	"""Wrapper around frappe.get_last_doc but does not throw"""
	try:
		return frappe.get_last_doc(*args, **kwargs)
	except Exception:
		return None


def cache(seconds: int, maxsize: int = 128, typed: bool = False):
	def wrapper_cache(func):
		func = functools.lru_cache(maxsize=maxsize, typed=typed)(func)
		func.delta = timedelta(seconds=seconds)
		func.expiration = datetime.utcnow() + func.delta

		@functools.wraps(func)
		def wrapped_func(*args, **kwargs):
			if datetime.utcnow() >= func.expiration:
				func.cache_clear()
				func.expiration = datetime.utcnow() + func.delta

			return func(*args, **kwargs)

		return wrapped_func

	return wrapper_cache


def chunk(iterable, size):
	"""Creates list of elements split into groups of n."""
	for i in range(0, len(iterable), size):
		yield iterable[i : i + size]  # noqa


@cache(seconds=1800)
def get_minified_script():
	migration_script = "../apps/cloud/cloud/scripts/migrate.py"
	script_contents = open(migration_script).read()
	return script_contents


@cache(seconds=1800)
def get_minified_script_2():
	migration_script = "../apps/cloud/cloud/scripts/migrate_2.py"
	script_contents = open(migration_script).read()
	return script_contents


def get_frappe_backups(url, email, password):
	return RemoteFrappeSite(url, email, password).get_backups()


class RemoteFrappeSite:
	def __init__(self, url, usr, pwd):
		if not url.startswith("http"):
			# http will be redirected to https in requests
			url = f"http://{url}"

		self.user_site = url
		self.user_login = usr
		self.password_login = pwd
		self._remote_backup_links = {}

		self._validate_frappe_site()
		self._validate_user_permissions()

	@property
	def user_sid(self):
		return self._user_sid

	@property
	def site(self):
		return self._site

	@property
	def backup_links(self):
		return self._remote_backup_links

	def _validate_frappe_site(self):
		"""Validates if Frappe Site and sets RemoteBackupRetrieval.site"""
		res = requests.get(f"{self.user_site}/api/method/frappe.ping")

		if not res.ok:
			frappe.throw("Invalid Frappe Site")

		if res.json().get("message") == "pong":
			url = res.url.split("/api")[0]
			self._site = url

	def _validate_user_permissions(self):
		"""Validates user permssions on Frappe Site and sets RemoteBackupRetrieval.user_sid"""
		response = requests.post(
			f"{self.site}/api/method/login",
			data={"usr": self.user_login, "pwd": self.password_login},
		)
		if not response.ok:
			if response.status_code == 401:
				frappe.throw("Invalid Credentials")
			else:
				response.raise_for_status()

		self._user_sid = response.cookies.get("sid")

	def _handle_backups_retrieval_failure(self, response):
		log_error(
			"Backups Retreival Error - Magic Migration",
			response=response.text,
			remote_site=self.site,
		)
		if response.status_code == 403:
			error_msg = "Insufficient Permissions"
		else:
			side = "Client" if 400 <= response.status_code < 500 else "Server"
			error_msg = (
				f"{side} Error occurred: {response.status_code} {response.raw.reason}"
				f" recieved from {self.site}"
			)
		frappe.throw(error_msg)

	def get_backups(self):
		self._create_fetch_backups_request()
		self._processed_backups_from_response()
		self._validate_missing_backups()

		return self.backup_links

	def _create_fetch_backups_request(self):
		headers = {"Accept": "application/json", "Content-Type": "application/json"}
		suffix = f"?sid={self.user_sid}" if self.user_sid else ""
		res = requests.get(
			f"{self.site}/api/method/frappe.utils.backups.fetch_latest_backups{suffix}",
			headers=headers,
		)
		if not res.ok:
			self._handle_backups_retrieval_failure(res)
		self._fetch_latest_backups_response = res.json().get("message", {})

	def _validate_missing_backups(self):
		missing_files = []

		for file_type, file_path in self.backup_links.items():
			if not file_path:
				missing_files.append(file_type)

		if missing_files:
			missing_config = "site config and " if not self.backup_links.get("config") else ""
			missing_backups = (
				f"Missing {missing_config}backup files:"
				f" {', '.join([x.title() for x in missing_files])}"
			)
			frappe.throw(missing_backups)

	def __process_frappe_url(self, path):
		if not path:
			return None
		backup_path = path.split("/private")[1]
		return urljoin(self.site, f"{backup_path}?sid={self.user_sid}")

	def _processed_backups_from_response(self):
		for file_type, file_path in self._fetch_latest_backups_response.items():
			self._remote_backup_links[file_type] = self.__process_frappe_url(file_path)


@site_cache(ttl=5 * 60)
def get_client_blacklisted_keys() -> list:
	"""Returns list of blacklisted Site Config Keys accessible to Press /dashboard users."""
	return list(
		set(
			[
				x.key
				for x in frappe.get_all("Site Config Key Blacklist", fields=["`key`"])
				+ frappe.get_all("Site Config Key", fields=["`key`"], filters={"internal": True})
			]
		)
	)


def sanitize_config(config: dict) -> dict:
	client_blacklisted_keys = get_client_blacklisted_keys()
	sanitized_config = config.copy()

	for key in config:
		if key in client_blacklisted_keys:
			sanitized_config.pop(key)

	return sanitized_config


def developer_mode_only():
	if not frappe.conf.developer_mode:
		frappe.throw("You don't know what you're doing. Go away!", frappe.ValidationError)


def human_readable(num: int) -> str:
	"""Assumes int data to describe size is in Bytes"""
	for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
		if abs(num) < 1024:
			return f"{num:3.1f}{unit}B"
		num /= 1024
	return f"{num:.1f}YiB"


def is_json(string):
	if isinstance(string, str):
		string = string.strip()
		return string.startswith("{") and string.endswith("}")
	elif isinstance(string, (dict, list)):
		return True


def guess_type(value):
	type_dict = {
		int: "Number",
		float: "Number",
		bool: "Boolean",
		dict: "JSON",
		list: "JSON",
		str: "String",
	}
	value_type = type(value)

	if value_type in type_dict:
		return type_dict[value_type]
	else:
		if is_json(value):
			return "JSON"
		return "String"


def convert(string):
	if isinstance(string, (dict, list)):
		return json.dumps(string)
	return string


def unique(seq, unique_by=None):
	"""Remove duplicates from a list based on an expression
	Usage:
	unique([{'x': 1, 'y': 2}, {'x': 1, 'y': 2}], lambda d: d['x'])
	# output: [{'x': 1, 'y': 2}]
	"""

	unique_by = unique_by or (lambda x: x)
	out = []
	seen = set()
	for d in seq:
		unique_key = unique_by(d)
		if unique_key not in seen:
			out.append(d)
			seen.add(unique_key)
	return out


def group_children_in_result(result, child_field_map):
	"""Usage:
	result =
	[
	{'name': 'test1', 'full_name': 'Faris Ansari', role: 'System Manager'},
	{'name': 'test1', 'full_name': 'Faris Ansari', role: 'Press Admin'},
	{'name': 'test2', 'full_name': 'Aditya Hase', role: 'Press Admin'},
	{'name': 'test2', 'full_name': 'Aditya Hase', role: 'Press Member'},
	]

	out = group_children_in_result(result, {'role': 'roles'})
	print(out)
	[
	{'name': 'test1', 'full_name': 'Faris Ansari', roles: ['System Manager', 'Press Admin']},
	{'name': 'test2', 'full_name': 'Aditya Hase', roles: ['Press Admin', 'Press Member']},
	]
	"""
	out = {}
	for d in result:
		out[d.name] = out.get(d.name) or d
		for child_field, target in child_field_map.items():
			out[d.name][target] = out[d.name].get(target) or []
			out[d.name][target].append(d.get(child_field))
			out[d.name].pop(child_field, "")
	return out.values()


def convert_user_timezone_to_utc(datetime):
	timezone = pytz.timezone(get_system_timezone())
	datetime_obj = get_datetime(datetime)
	return timezone.localize(datetime_obj).astimezone(pytz.utc).isoformat()


class ttl_cache:
	"""
	Does not invalidate cache depending on function
	args. Ideally it's for functions with 0 arity.

	Example:

	# or use it as a decorator
	cached_func = ttl_cache()(func)

	# to invalidate cache
	cached_func.cache.invalidate()
	"""

	def __init__(self, ttl: int = 60):
		self.ttl = ttl
		self.result = None
		self.start = 0

	def invalidate(self):
		self.result = None
		self.start = 0

	def __call__(self, func):
		self.result = None
		self.start = time.time()

		def wrapper_func(*args, **kwargs):
			if self.result is not None and (time.time() - self.start) < self.ttl:
				return self.result
			self.start = time.time()
			self.result = func(*args, **kwargs)
			return self.result

		wrapper_func.cache = self
		return wrapper_func


def poly_get_doctype(doctypes, name):
	"""Get the doctype value from the given name of a doc from a list of doctypes"""
	for doctype in doctypes:
		if frappe.db.exists(doctype, name):
			return doctype
	return doctypes[-1]


def reconnect_on_failure():
	@wrapt.decorator
	def wrapper(wrapped, instance, args, kwargs):
		try:
			return wrapped(*args, **kwargs)
		except InterfaceError:
			frappe.db.connect()
			return wrapped(*args, **kwargs)

	return wrapper


def get_filepath(root: str, filename: str, max_depth: int = 1):
	"""
	Returns the absolute path of a `filename` under `root`. If
	it is not found, returns None.

	Example: get_filepath("apps/hrms", "hooks.py", 2)

	Depth of search under file tree can be set using `max_depth`.
	"""
	path = _get_filepath(
		Path(root),
		filename,
		max_depth,
	)

	if path is None:
		return path

	return path.absolute().as_posix()


def _get_filepath(root: Path, filename: str, max_depth: int) -> Path | None:
	if root.name == filename:
		return root
	if max_depth == 0 or not root.is_dir():
		return None
	for new_root in root.iterdir():
		if possible_path := _get_filepath(
			new_root,
			filename,
			max_depth - 1,
		):
			return possible_path
