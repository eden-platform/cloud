<template>
	<Dialog
		v-if="source"
		:options="{
			title: 'Add New App Release',
			actions: [
				{
					label: 'Change Branch',
					variant: 'solid',
					loading: $resources.changeBranch.loading,
					onClick: () => $resources.changeBranch.submit()
				}
			]
		}"
		:modelValue="show"
	>
		<template v-slot:body-content>
			<select class="form-select block w-full" v-model="selectedBranch">
				<option v-for="branch in branchList()" :key="branch">
					{{ branch }}
				</option>
			</select>
		</template>
	</Dialog>
</template>

<script>
export default {
	name: 'ChangeAppBranchDialog',
	data() {
		return {
			selectedBranch: null
		};
	},
	props: ['show', 'app', 'source', 'version', 'activeBranch'],
	resources: {
		branches() {
			return {
				url: 'cloud.api.marketplace.branches',
				params: {
					name: this.source
				},
				auto: true
			};
		},
		changeBranch() {
			return {
				url: 'cloud.api.marketplace.change_branch',
				params: {
					name: this.app,
					source: this.source,
					version: this.version,
					to_branch: this.selectedBranch
				},
				onSuccess() {
					window.location.reload();
				},
				validate() {
					if (this.selectedBranch == this.app.branch) {
						return 'Please select a different branch';
					}
				}
			};
		}
	},
	methods: {
		branchList() {
			if (this.$resources.branches.loading || !this.$resources.branches.data) {
				return [];
			}
			return this.$resources.branches.data.map(d => d.name);
		}
	},
	mounted() {
		this.selectedBranch = this.activeBranch;
	}
};
</script>
