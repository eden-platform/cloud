<template>
	<Card title="Credit Balance" subtitle="History of your credit balance">
		<div class="max-h-96 divide-y">
			<div
				class="grid grid-cols-4 items-center gap-x-8 py-4 text-base text-gray-600 md:grid-cols-4"
			>
				<span class="hidden md:inline">Date</span>
				<span class="col-span-2 md:col-span-1">Description</span>
				<span>Amount</span>
				<span>Balance</span>
			</div>
			<div
				class="grid grid-cols-4 items-center gap-x-8 py-4 text-base text-gray-900 md:grid-cols-4"
				v-for="d in $resources.balances.data"
				:key="d.name"
			>
				<div class="hidden md:block">
					{{ formatDate(d) }}
				</div>
				<div class="col-span-2 whitespace-nowrap text-gray-700 md:col-span-1">
					<div>
						{{ getDescription(d) }}
					</div>
					<div class="md:hidden">{{ formatDate(d) }}</div>
				</div>
				<div class="whitespace-nowrap text-gray-700">
					{{ d.formatted.amount }}
				</div>
				<div class="whitespace-nowrap">{{ d.formatted.ending_balance }}</div>
			</div>
		</div>
	</Card>
</template>
<script>
export default {
	name: 'AccountBillingCreditBalance',
	resources: {
		balances: 'cloud.api.billing.balances'
	},
	methods: {
		formatDate(d) {
			return this.$date(d.creation).toLocaleString({
				month: 'long',
				day: 'numeric',
				year: 'numeric'
			});
		},
		getDescription(d) {
			if (d.type === 'Applied To Invoice' && d.formatted.invoice_for) {
				return `Invoice For ${d.formatted.invoice_for}`;
			}

			return d.amount < 0 ? d.type : d.source;
		}
	}
};
</script>
