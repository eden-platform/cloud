<template>
	<div class="mt-2 space-y-2 divide-y">
		<AppUpdateCard
			v-for="(app, index) in appsWithUpdates"
			:key="app.app"
			@click.native.self="toggleApp(app)"
			v-model:app="appsWithUpdates[index]"
			:selected="selectedApps.map(a => a.app).includes(app.app)"
			:uninstall="false"
			:selectable="true"
		/>
		<AppUpdateCard
			v-for="(app, index) in removedApps"
			:key="app.name"
			@click.native.self="toggleApp(app)"
			v-model:app="removedApps[index]"
			:selected="selectedApps.map(a => a.app).includes(app.app)"
			:uninstall="true"
		/>
	</div>
</template>
<script>
import AppUpdateCard from './AppUpdateCard.vue';

export default {
	name: 'BenchAppUpdates',
	props: ['apps', 'removedApps'],
	components: {
		AppUpdateCard
	},
	data() {
		return {
			selectedApps: []
		};
	},
	mounted() {
		// Select all apps by default
		this.selectedApps = this.appsWithUpdates.map(a => {
			return { app: a.app, release: a.next_release };
		});
		this.$emit('update:selectedApps', this.selectedApps);
	},
	methods: {
		toggleApp(app) {
			if (!this.selectedApps.map(a => a.app).includes(app.app)) {
				this.selectedApps.push({ app: app.app, release: app.next_release });
				this.$emit('update:selectedApps', this.selectedApps);
			} else {
				this.selectedApps = this.selectedApps.filter(a => a.app !== app.app);
				this.$emit('update:selectedApps', this.selectedApps);
			}
		}
	},
	computed: {
		appsWithUpdates() {
			return this.apps.filter(app => app.update_available);
		}
	},
	watch: {
		appsWithUpdates: {
			handler(apps) {
				apps.map(app => {
					this.selectedApps
						.filter(a => a.app == app.app)
						.map(a => (a.release = app.next_release));
				});
			},
			deep: true,
			immediate: true
		},
		removedApps: {
			handler(apps) {
				apps.map(app => {
					this.selectedApps
						.filter(a => a.app == app.app)
						.map(a => (a.release = app.next_release));
				});
			},
			deep: true,
			immediate: true
		},
		selectedApps: {
			handler(apps) {
				// Hardcoded for now, need a better way
				// to manage such dependencies (#TODO)
				// If updating ERPNext, must update Eden with it

				let frappeApp = this.apps.filter(a => a.app == 'frappe');
				let frappeUpdateAvailable =
					frappeApp.length == 1 && frappeApp[0].update_available;

				if (
					apps.map(a => a.app).includes('erpnext') &&
					!apps.map(a => a.app).includes('frappe') &&
					frappeUpdateAvailable
				) {
					apps.push({ app: 'frappe', release: frappeApp[0].next_release });
				}
			},
			deep: true,
			immediate: true
		}
	}
};
</script>
