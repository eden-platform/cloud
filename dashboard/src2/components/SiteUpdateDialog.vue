<template>
	<Dialog
		v-model="show"
		:options="{
			title: 'Updates Available',
			size: '2xl'
		}"
	>
		<template #body-content>
			<template v-if="updatableApps.length > 0">
				<GenericList :options="listOptions" />
				<div class="mt-4 flex flex-col space-y-4">
					<DateTimeControl v-model="scheduledTime" label="Schedule Time" />
					<div class="flex flex-col space-y-2">
						<FormControl
							label="Skip failing patches if any"
							type="checkbox"
							v-model="skipFailingPatches"
						/>
						<FormControl
							label="Skip taking backup for this update (If the update fails, rollback will not occur)"
							type="checkbox"
							v-model="skipBackups"
						/>
					</div>
				</div>
			</template>
			<div v-else class="text-center text-base text-gray-600">
				No apps to update
			</div>
			<ErrorMessage class="mt-4" :message="$site.scheduleUpdate.error" />
		</template>
		<template #actions>
			<Button
				class="w-full"
				variant="solid"
				:loading="$site.scheduleUpdate.loading"
				:label="`Update ${
					scheduledTime ? `at ${scheduledTimeInLocal}` : 'Now'
				}`"
				@click="
					$site.scheduleUpdate.submit(
						{
							skip_failing_patches: skipFailingPatches,
							skip_backups: skipBackups,
							scheduled_time: scheduledTimeInIST
						},
						{
							onSuccess: () => {
								$site.reload();
								show = false;
								$router.push({ name: 'Site Detail Updates' });
							}
						}
					)
				"
			/>
		</template>
	</Dialog>
</template>
<script>
import { getCachedDocumentResource } from 'frappe-ui';
import DateTimeControl from './DateTimeControl.vue';
import GenericList from './GenericList.vue';
import dayjs, { dayjsIST } from '../utils/dayjs';

export default {
	name: 'SiteUpdateDialog',
	props: ['site'],
	components: {
		GenericList,
		DateTimeControl
	},
	data() {
		return {
			show: true,
			skipFailingPatches: false,
			scheduledTime: '',
			skipBackups: false
		};
	},
	methods: {
		twoseconds() {
			return new Promise(resolve => {
				setTimeout(() => {
					resolve();
				}, 2000);
			});
		}
	},
	computed: {
		scheduledTimeInIST() {
			if (!this.scheduledTime) return;
			return dayjsIST(this.scheduledTime).format('YYYY-MM-DDTHH:mm');
		},
		scheduledTimeInLocal() {
			return dayjs(this.scheduledTime).format('lll');
		},
		listOptions() {
			return {
				data: this.updatableApps.filter(
					app => app.current_hash !== app.next_hash
				),
				columns: [
					{
						label: 'App',
						fieldname: 'app',
						format(value, row) {
							return row.title || value;
						}
					},
					{
						label: 'Current Version',
						type: 'Badge',
						format(value, row) {
							return row.will_branch_change
								? row.current_branch
								: row.current_tag || row.current_hash.slice(0, 7);
						},
						link(value, row) {
							if (row.will_branch_change) {
								return `${row.repository_url}/tree/${row.current_branch}`;
							}
							if (row.current_tag) {
								return `${row.repository_url}/releases/tag/${row.current_tag}`;
							}
							if (row.current_hash) {
								return `${row.repository_url}/commit/${row.current_hash}`;
							}
						}
					},
					{
						label: 'Next Version',
						type: 'Badge',
						format(value, row) {
							return row.will_branch_change
								? row.next_branch
								: row.next_tag || row.next_hash.slice(0, 7);
						},
						link(value, row) {
							if (row.will_branch_change) {
								return `${row.repository_url}/tree/${row.next_branch}`;
							}
							if (row.next_tag) {
								return `${row.repository_url}/releases/tag/${row.next_tag}`;
							}
							if (row.next_hash) {
								return `${row.repository_url}/commit/${row.next_hash}`;
							}
						}
					}
				]
			};
		},
		updatableApps() {
			if (!this.$site.doc.update_information.update_available) return [];
			let installedApps = this.$site.doc.update_information.installed_apps.map(
				d => d.app
			);
			return this.$site.doc.update_information.apps.filter(app =>
				installedApps.includes(app.app)
			);
		},
		$site() {
			return getCachedDocumentResource('Site', this.site);
		}
	}
};
</script>
