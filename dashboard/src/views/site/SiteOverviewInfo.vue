<template>
	<Card title="Site Info" subtitle="General information about your site">
		<div class="divide-y">
			<div class="flex items-center py-3">
				<Avatar
					v-if="info.owner"
					:image="info.owner.user_image"
					:label="info.owner.first_name"
				/>
				<div class="ml-3 flex flex-1 items-center justify-between">
					<div>
						<div class="text-base text-gray-600">Owned By</div>
						<div class="text-base font-medium text-gray-900">
							{{ info.owner.first_name }}
							{{ info.owner.last_name }}
						</div>
					</div>
					<div class="text-right">
						<div class="text-base text-gray-600">Created On</div>
						<div class="text-base font-medium text-gray-900">
							{{ formatDate(info.created_on, 'DATE_FULL') }}
						</div>
					</div>
					<div v-if="info.last_deployed" class="text-right">
						<div class="text-base text-gray-600">Last Deployed</div>

						<div class="text-base font-medium text-gray-900">
							{{
								$date(info.last_deployed).toLocaleString({
									month: 'long',
									day: 'numeric'
								})
							}}
						</div>
					</div>
				</div>
			</div>

			<ListItem
				v-if="site.group && site.status !== 'Pending'"
				title="Auto Update Site"
				class="overflow-x-hidden"
				description="Automatically schedule site updates whenever available"
			>
				<template v-slot:actions>
					<LoadingIndicator class="h-4 w-4" v-if="loading" />
					<input
						v-show="!loading"
						id="auto-update-checkbox"
						@input="changeAutoUpdateSettings"
						type="checkbox"
						class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
					/>
				</template>
			</ListItem>
			<ListItem
				v-if="site.status == 'Active'"
				title="Deactivate Site"
				description="The site will go inactive and won't be publicly accessible"
			>
				<template v-slot:actions>
					<Tooltip
						:text="
							!permissions.deactivate
								? `You don't have enough permissions to perform this action`
								: 'Deactivate Site'
						"
					>
						<Button
							@click="onDeactivateClick"
							class="shrink-0"
							:disabled="!permissions.deactivate"
						>
							Deactivate Site
						</Button>
					</Tooltip>
				</template>
			</ListItem>

			<ListItem
				v-if="['Inactive', 'Broken'].includes(site.status)"
				title="Activate Site"
				description="The site will become active and will be accessible"
			>
				<template v-slot:actions>
					<Button
						@click="onActivateClick"
						class="shrink-0"
						:variant="site.status === 'Broken' ? 'solid' : 'subtle'"
					>
						Activate Site
					</Button>
				</template>
			</ListItem>

			<ListItem
				v-if="site.status !== 'Pending'"
				title="Drop Site"
				description="Once you drop site your site, there is no going back"
			>
				<template v-slot:actions>
					<SiteDrop :site="site" v-slot="{ showDialog }">
						<Tooltip
							:text="
								!permissions.drop
									? `You don't have enough permissions to perform this action`
									: 'Drop Site'
							"
						>
							<Button
								theme="red"
								:disabled="!permissions.drop"
								@click="showDialog"
							>
								Drop Site
							</Button>
						</Tooltip>
					</SiteDrop>
				</template>
			</ListItem>
		</div>
	</Card>
</template>
<script>
import SiteDrop from './SiteDrop.vue';
import { notify } from '@/utils/toast';

export default {
	name: 'SiteOverviewInfo',
	props: ['site', 'info'],
	components: { SiteDrop },
	data() {
		return {
			loading: false
		};
	},
	mounted() {
		const autoUpdateCheckbox = document.getElementById('auto-update-checkbox');

		if (autoUpdateCheckbox) {
			autoUpdateCheckbox.checked = this.info.auto_updates_enabled;
		}
	},
	methods: {
		changeAutoUpdateSettings(event) {
			event.preventDefault();
			this.loading = true;

			return this.$call('cloud.api.site.change_auto_update', {
				name: this.site.name,
				auto_update_enabled: event.target.checked
			}).then(() => {
				setTimeout(() => window.location.reload(), 1000);
			});
		},
		onDeactivateClick() {
			this.$confirm({
				title: 'Deactivate Site',
				message: `
					Are you sure you want to deactivate this site? The site will go in an inactive state.
					It won't be accessible and background jobs won't run. You will <strong>still be charged</strong> for it.
				`,
				actionLabel: 'Deactivate',
				actionColor: 'red',
				action: () => this.deactivate()
			});
		},
		onActivateClick() {
			this.$confirm({
				title: 'Activate Site',
				message: `Are you sure you want to activate this site?
				<br><br><strong>Note: Use this as last resort if site is broken and inaccessible</strong>`,
				actionLabel: 'Activate',
				action: () => this.activate()
			});
		},
		deactivate() {
			return this.$call('cloud.api.site.deactivate', {
				name: this.site.name
			}).then(() => {
				setTimeout(() => window.location.reload(), 1000);
			});
		},
		activate() {
			this.$call('cloud.api.site.activate', {
				name: this.site.name
			});
			notify({
				title: 'Site activated successfully!',
				message: 'You can now access your site',
				icon: 'check',
				color: 'green'
			});
			setTimeout(() => window.location.reload(), 1000);
		}
	},
	computed: {
		permissions() {
			return {
				drop: this.$account.hasPermission(
					this.site.name,
					'cloud.api.site.archive'
				),
				deactivate: this.$account.hasPermission(
					this.site.name,
					'cloud.api.site.deactivate'
				)
			};
		}
	}
};
</script>
