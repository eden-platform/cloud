<template>
	<div class="shrink-0">
		<slot v-bind="{ showDialog }"></slot>
		<Dialog
			:options="{
				title: 'Drop Server',
				actions: [
					{
						label: 'Drop Server',
						variant: 'solid',
						theme: 'red',
						loading: $resources.dropServer.loading,
						onClick: () => $resources.dropServer.submit()
					}
				]
			}"
			v-model="dialogOpen"
		>
			<template v-slot:body-content>
				<p class="text-base">
					Are you sure you want to drop your server? The server will be archived
					and all of the benches and sites on it will be deleted. This action
					cannot be undone.
				</p>
				<p class="mt-4 text-base">
					Please type
					<span class="font-semibold">{{ server.name }}</span> to confirm.
				</p>
				<FormControl class="mt-4 w-full" v-model="confirmServerName" />
				<ErrorMessage class="mt-2" :message="$resources.dropServer.error" />
			</template>
		</Dialog>
	</div>
</template>

<script>
export default {
	name: 'ServerDrop',
	props: ['server'],
	data() {
		return {
			dialogOpen: false,
			confirmServerName: null
		};
	},
	resources: {
		dropServer() {
			return {
				url: 'cloud.api.server.archive',
				params: {
					name: this.server?.name
				},
				onSuccess() {
					this.dialogOpen = false;
					this.$router.push('/servers');
				},
				validate() {
					if (this.server?.name !== this.confirmServerName) {
						return 'Please type the server name to confirm';
					}
				}
			};
		}
	},
	methods: {
		showDialog() {
			this.dialogOpen = true;
		}
	}
};
</script>
