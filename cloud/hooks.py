# -*- coding: utf-8 -*-
from cloud.api.account import get_frappe_io_auth_url

from . import __version__ as app_version

app_name = "cloud"
app_title = "Cloud"
app_publisher = "Frappe"
app_description = "Managed Frappe Hosting"
app_icon = "octicon octicon-rocket"
app_color = "grey"
app_email = "aditya@frappe.io"
app_license = "GNU Affero General Public License v3.0"
version = app_version

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/cloud/css/cloud.css"
# app_include_js = "/assets/cloud/js/cloud.js"
app_include_js = [
	"cloud.bundle.js",
]

# include js, css files in header of web template
# web_include_css = "/assets/cloud/css/cloud.css"
# web_include_js = "/assets/cloud/js/cloud.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "cloud.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

look_for_sidebar_json = True

base_template_map = {
	r"docs.*": "templates/doc.html",
	r"internal.*": "templates/doc.html",
}

update_website_context = ["cloud.overrides.update_website_context"]

website_route_rules = [
	{"from_route": "/dashboard/<path:app_path>", "to_route": "dashboard"},
]

website_redirects = [
	{"source": "/dashboard/f-login", "target": get_frappe_io_auth_url() or "/"},
	{"source": "/f-login", "target": "/dashboard/f-login"},
	{"source": "/signup", "target": "/erpnext/signup"},
]

email_css = ["/assets/cloud/css/email.css"]

jinja = {
	"filters": ["cloud.cloud.doctype.marketplace_app.utils.number_k_format"],
	"methods": ["cloud.utils.get_country_info"],
}

# Installation
# ------------

# before_install = "cloud.install.before_install"
after_install = "cloud.install.after_install"
after_migrate = ["cloud.api.account.clear_country_list_cache", "cloud.sanity.checks"]

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

notification_config = "cloud.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
	"Site": "cloud.cloud.doctype.site.site.get_permission_query_conditions",
	"Site Domain": (
		"cloud.cloud.doctype.site_domain.site_domain.get_permission_query_conditions"
	),
	"TLS Certificate": "cloud.cloud.doctype.tls_certificate.tls_certificate.get_permission_query_conditions",
	"Team": "cloud.cloud.doctype.team.team.get_permission_query_conditions",
	"Subscription": (
		"cloud.cloud.doctype.subscription.subscription.get_permission_query_conditions"
	),
	"Stripe Payment Method": "cloud.cloud.doctype.stripe_payment_method.stripe_payment_method.get_permission_query_conditions",
	"Balance Transaction": "cloud.cloud.doctype.balance_transaction.balance_transaction.get_permission_query_conditions",
	"Invoice": "cloud.cloud.doctype.invoice.invoice.get_permission_query_conditions",
	"App Source": (
		"cloud.cloud.doctype.app_source.app_source.get_permission_query_conditions"
	),
	"App Release": (
		"cloud.cloud.doctype.app_release.app_release.get_permission_query_conditions"
	),
	"Release Group": "cloud.cloud.doctype.release_group.release_group.get_permission_query_conditions",
	"Deploy Candidate": "cloud.cloud.doctype.deploy_candidate.deploy_candidate.get_permission_query_conditions",
	"Deploy Candidate Difference": "cloud.cloud.doctype.deploy_candidate_difference.deploy_candidate_difference.get_permission_query_conditions",
	"Deploy": "cloud.cloud.doctype.deploy.deploy.get_permission_query_conditions",
	"Bench": "cloud.cloud.doctype.bench.bench.get_permission_query_conditions",
	"Server": "cloud.cloud.doctype.server.server.get_permission_query_conditions",
	"Database Server": "cloud.cloud.doctype.database_server.database_server.get_permission_query_conditions",
	"Virtual Machine": "cloud.cloud.doctype.virtual_machine.virtual_machine.get_permission_query_conditions",
}
has_permission = {
	"Site": "cloud.overrides.has_permission",
	"Site Domain": "cloud.overrides.has_permission",
	"TLS Certificate": "cloud.overrides.has_permission",
	"Team": "cloud.cloud.doctype.team.team.has_permission",
	"Subscription": "cloud.overrides.has_permission",
	"Stripe Payment Method": "cloud.overrides.has_permission",
	"Balance Transaction": "cloud.overrides.has_permission",
	"Invoice": "cloud.overrides.has_permission",
	"App Source": "cloud.overrides.has_permission",
	"App Release": "cloud.cloud.doctype.app_release.app_release.has_permission",
	"Release Group": "cloud.overrides.has_permission",
	"Deploy Candidate": "cloud.overrides.has_permission",
	"Deploy Candidate Difference": "cloud.overrides.has_permission",
	"Deploy": "cloud.overrides.has_permission",
	"Bench": "cloud.overrides.has_permission",
	"Server": "cloud.overrides.has_permission",
	"Database Server": "cloud.overrides.has_permission",
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Stripe Webhook Log": {
		"after_insert": [
			"cloud.cloud.doctype.invoice.stripe_webhook_handler.handle_stripe_webhook_events",
			"cloud.cloud.doctype.team.team.process_stripe_webhook",
		],
	},
	"Address": {"validate": "cloud.api.billing.validate_gst"},
	"Site": {"before_insert": "cloud.cloud.doctype.team.team.validate_site_creation"},
	"Marketplace App Subscription": {
		"on_update": "cloud.cloud.doctype.storage_integration_subscription.storage_integration_subscription.create_after_insert",
	},
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    "weekly_long": [
		"cloud.cloud.doctype.marketplace_app.events.auto_review_for_missing_steps"
	],
	"daily": [
		"cloud.experimental.doctype.referral_bonus.referral_bonus.credit_referral_bonuses",
		"cloud.cloud.doctype.log_counter.log_counter.record_counts",
	],
	"daily_long": [
		"cloud.cloud.audit.check_bench_fields",
		"cloud.cloud.audit.check_offsite_backups",
		"cloud.cloud.audit.check_backup_records",
		"cloud.cloud.audit.check_app_server_replica_benches",
		"cloud.cloud.doctype.invoice.invoice.finalize_unpaid_prepaid_credit_invoices",
		"cloud.cloud.doctype.bench.bench.sync_analytics",
		"cloud.saas.doctype.saas_app_subscription.saas_app_subscription.suspend_prepaid_subscriptions",
		"cloud.cloud.doctype.payout_order.payout_order.create_marketplace_payout_orders",
		"cloud.cloud.doctype.root_domain.root_domain.cleanup_cname_records",
		"cloud.cloud.doctype.remote_file.remote_file.poll_file_statuses",
		"cloud.cloud.doctype.virtual_machine.virtual_machine.snapshot_virtual_machines",
		"cloud.doctype.site_domain.site_domain.update_dns_type",
	],
	"hourly": [
		"cloud.cloud.doctype.site.backups.cleanup_local",
		"cloud.cloud.doctype.agent_job.agent_job.update_job_step_status",
		"cloud.cloud.doctype.bench.bench.archive_obsolete_benches",
		"cloud.cloud.doctype.site.backups.schedule_for_sites_with_backup_time",
		"cloud.doctype.tls_certificate.tls_certificate.renew_tls_certificates",
	],
	"hourly_long": [
        "cloud.cloud.doctype.release_group.release_group.prune_servers_without_sites",
		"cloud.cloud.doctype.server.server.scale_workers",
		"cloud.cloud.doctype.usage_record.usage_record.link_unlinked_usage_records",
		"cloud.cloud.doctype.bench.bench.sync_benches",
		"cloud.cloud.doctype.invoice.invoice.finalize_draft_invoices",
		"cloud.cloud.doctype.app.app.poll_new_releases",
		"cloud.cloud.doctype.agent_job.agent_job.fail_old_jobs",
		"cloud.cloud.doctype.site_update.site_update.mark_stuck_updates_as_fatal",
		"cloud.cloud.doctype.deploy_candidate.deploy_candidate.cleanup_build_directories",
		"cloud.cloud.doctype.deploy_candidate.deploy_candidate.delete_draft_candidates",
        "cloud.cloud.doctype.deploy_candidate.deploy_candidate.check_builds_status",
		"cloud.cloud.doctype.virtual_disk_snapshot.virtual_disk_snapshot.delete_old_snapshots",
		"cloud.cloud.doctype.app_release.app_release.cleanup_unused_releases",
	],
	"all": [
		"cloud.auth.flush",
        "cloud.cloud.doctype.site.sync.sync_setup_wizard_status",

	],
	"cron": {
		"1-59/2 * * * *": [
			"cloud.cloud.doctype.incident.incident.validate_incidents",
		],
		"*/2 * * * *": [
			"cloud.cloud.doctype.incident.incident.resolve_incidents",
		],
		"0 4 * * *": [
			"cloud.cloud.doctype.site.backups.cleanup_offsite",
			"cloud.cloud.cleanup.unlink_remote_files_from_site",
		],
		"0 3 * * *": [
			"cloud.cloud.doctype.drip_email.drip_email.send_drip_emails",
		],
		"* * * * * 0/5": [
			"cloud.cloud.doctype.agent_job.agent_job.poll_pending_jobs",
			"cloud.cloud.doctype.telegram_message.telegram_message.send_telegram_message",
		],
		"0 */6 * * *": [
			"cloud.cloud.doctype.server.server.cleanup_unused_files",
			"cloud.cloud.doctype.razorpay_payment_record.razorpay_payment_record.fetch_pending_payment_orders",
		],
		"30 * * * *": ["cloud.cloud.doctype.agent_job.agent_job.suspend_sites"],
		"*/15 * * * *": [
			"cloud.cloud.doctype.site_update.site_update.schedule_updates",
			"cloud.cloud.doctype.drip_email.drip_email.send_welcome_email",
			"cloud.cloud.doctype.site.backups.schedule",
			"cloud.cloud.doctype.site_update.site_update.run_scheduled_updates",
			"cloud.cloud.doctype.site_migration.site_migration.run_scheduled_migrations",
			"cloud.cloud.doctype.version_upgrade.version_upgrade.run_scheduled_upgrades",
			"cloud.cloud.doctype.subscription.subscription.create_usage_records",
			"cloud.cloud.doctype.virtual_machine.virtual_machine.sync_virtual_machines",
			"cloud.cloud.doctype.mariadb_stalk.mariadb_stalk.fetch_stalks",
		],
		"*/5 * * * *": [
			"cloud.cloud.doctype.version_upgrade.version_upgrade.update_from_site_update",
			"cloud.cloud.doctype.site_replication.site_replication.update_from_site",
			"cloud.cloud.doctype.virtual_disk_snapshot.virtual_disk_snapshot.sync_snapshots",
		],
		"* * * * *": [
			"cloud.cloud.doctype.deploy_candidate.deploy_candidate.run_scheduled_builds",
		],
		"*/10 * * * *": [
			"cloud.saas.doctype.saas_product.saas_product.replenish_standby_sites",
			"cloud.cloud.doctype.site.saas_pool.create",
		],
		"*/30 * * * *": [
			"cloud.cloud.doctype.site_update.scheduled_auto_updates.trigger",
			"cloud.cloud.doctype.team.suspend_sites.execute",
		],
		"15,45 * * * *": [
			"cloud.cloud.doctype.site.site_usages.update_cpu_usages",
			"cloud.cloud.doctype.site.site_usages.update_disk_usages",
		],
		"15 2,4 * * *": [
			"cloud.cloud.doctype.team_deletion_request.team_deletion_request.process_team_deletion_requests",
		],
		"0 0 1 */3 *": [
			"cloud.cloud.doctype.backup_restoration_test.backup_test.run_backup_restore_test"
		],
		"0 8 * * *": [
			"cloud.cloud.audit.billing_audit",
			"cloud.cloud.audit.partner_billing_audit",
		],
		"0 6 * * *": [
			"cloud.cloud.audit.suspend_sites_with_disabled_team",
			"cloud.cloud.doctype.tls_certificate.tls_certificate.retrigger_failed_wildcard_tls_callbacks",
		],
	},
}

deploy_hours = [1, 2, 3, 4, 5, 21, 22, 23]  # Purposefully avoiding 0

fixtures = [
	"Agent Job Type",
	"Cloud Job Type",
	"Frappe Version",
	"MariaDB Variable",
	"Cloud Region",
	{"dt": "Role", "filters": [["role_name", "like", "Cloud%"]]},
	"Site Config Key Blacklist",
	"Cloud Method Permission",
	"Bench Dependency",
]
# Testing
# -------

before_tests = "cloud.tests.before_test.execute"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {"upload_file": "cloud.overrides.upload_file"}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "cloud.task.get_dashboard_data"
# }

override_doctype_class = {"User": "cloud.overrides.CustomUser"}

on_session_creation = "cloud.overrides.on_session_creation"
# on_logout = "cloud.overrides.on_logout"

before_request = "cloud.overrides.before_request"
before_job = "cloud.overrides.before_job"
after_job = "cloud.overrides.after_job"

# Data Deletion Privacy Docs

user_data_fields = [
	{"doctype": "Team", "strict": True},
]

auth_hooks = ["cloud.auth.hook"]

page_renderer = ["cloud.metrics.MetricsRenderer"]

export_python_type_annotations = True
