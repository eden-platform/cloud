<template>
	<EdenUIBadge :label="label" :theme="_color" />
</template>

<script>
import { Badge as EdenUIBadge } from 'frappe-ui';

export default {
	name: 'Badge',
	props: ['label', 'theme'],
	components: {
		EdenUIBadge
	},
	computed: {
		_color() {
			if (this.theme) return this.theme;
			return {
				Approved: 'green',
				Broken: 'red',
				Installing: 'orange',
				Running: 'blue',
				Pending: 'orange',
				Failure: 'red',
				'Update Available': 'blue',
				Enabled: 'blue',
				'Awaiting Approval': 'orange',
				'Awaiting Deploy': 'orange',
				Success: 'green',
				Completed: 'green',
				Deployed: 'green',
				Expired: 'red',
				Paid: 'green',
				Unpaid: 'orange',
				'Invoice Created': 'blue',
				Rejected: 'red',
				'In Review': 'orange',
				'Attention Required': 'red',
				Active: 'green',
				Trial: 'orange',
				Published: 'green',
				Owner: 'blue',
				Primary: 'green',
				'Latest Deployed': 'orange',
				'Not Deployed': 'orange',
				'Action Required': 'red',
				'First Deploy': 'green',
				'Will be Uninstalled': 'red'
			}[this.label];
		}
	}
};
</script>
