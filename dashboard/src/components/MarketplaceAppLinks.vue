<template>
	<Card title="Links" subtitle="Will be shown in marketplace">
		<template #actions>
			<Button icon-left="edit" @click="showEditLinksDialog = true">Edit</Button>
		</template>
		<Dialog
			:options="{
				title: 'Update Links',
				actions: [
					{
						variant: 'solid',
						label: 'Save Changes',
						loading: $resources.updateAppLinks.loading,
						onClick: () => $resources.updateAppLinks.submit()
					}
				]
			}"
			v-model="showEditLinksDialog"
		>
			<template v-slot:body-content>
				<div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
					<FormControl label="Website" v-model="app.website" />
					<FormControl label="Support" v-model="app.support" />
					<FormControl label="Documentation" v-model="app.documentation" />
					<FormControl label="Privacy Policy" v-model="app.privacy_policy" />
					<FormControl
						label="Terms of Service"
						v-model="app.terms_of_service"
					/>
				</div>

				<ErrorMessage class="mt-4" :message="$resources.updateAppLinks.error" />
			</template>
		</Dialog>
		<div class="divide-y" v-if="app">
			<ListItem
				title="Website"
				:description="$sanitize(app.website || 'N/A')"
			/>
			<ListItem
				title="Support"
				:description="$sanitize(app.support || 'N/A')"
			/>
			<ListItem
				title="Documentation"
				:description="$sanitize(app.documentation || 'N/A')"
			/>
			<ListItem
				title="Privacy Policy"
				:description="$sanitize(app.privacy_policy || 'N/A')"
			/>
			<ListItem
				title="Terms of Service"
				:description="$sanitize(app.terms_of_service || 'N/A')"
			/>
		</div>
	</Card>
</template>

<script>
import { notify } from '@/utils/toast';

export default {
	name: 'MarketplaceAppLinks',
	props: {
		app: Object
	},
	data() {
		return {
			showEditLinksDialog: false
		};
	},
	resources: {
		updateAppLinks() {
			return {
				url: 'cloud.api.marketplace.update_app_links',
				params: {
					name: this.app.name,
					links: {
						website: this.app.website,
						support: this.app.support,
						documentation: this.app.documentation,
						privacy_policy: this.app.privacy_policy,
						terms_of_service: this.app.terms_of_service
					}
				},
				onSuccess() {
					this.showEditLinksDialog = false;
					notify({
						title: 'Links Updated!',
						icon: 'check',
						color: 'green'
					});
				}
			};
		}
	}
};
</script>
