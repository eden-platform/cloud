<template>
	<div>
		<label class="text-lg font-semibold"> Choose a Hostname </label>
		<p class="text-base text-gray-700">
			Give your code server a unique name. It can only contain alphanumeric
			characters and dashes.
		</p>
		<div class="mt-4 flex">
			<input
				class="form-input z-10 w-full rounded-r-none"
				type="text"
				:value="modelValue"
				placeholder="subdomain"
				@change="subdomainChange"
			/>
			<div class="flex items-center rounded-r bg-gray-100 px-4 text-base">
				.{{ domain }}
			</div>
		</div>
		<div class="mt-1">
			<div
				v-if="subdomainAvailable"
				class="text-sm text-green-600"
				role="alert"
			>
				{{ modelValue }}.{{ domain }} is available
			</div>
			<ErrorMessage :message="errorMessage" />
		</div>
	</div>
</template>
<script>
export default {
	name: 'Hostname',
	props: ['modelValue', 'domain'],
	emits: ['update:modelValue', 'error'],
	data() {
		return {
			subdomainAvailable: false,
			errorMessage: null
		};
	},
	methods: {
		async subdomainChange(e) {
			let subdomain = e.target.value;
			this.$emit('update:modelValue', subdomain);
			this.subdomainAvailable = false;

			let error = this.validateSubdomain(subdomain);
			if (!error) {
				let subdomainTaken = await this.$call('cloud.api.spaces.exists', {
					subdomain,
					domain: this.domain
				});
				if (subdomainTaken) {
					error = `${subdomain}.${this.domain} already exists.`;
				} else {
					this.subdomainAvailable = true;
				}
			}
			this.errorMessage = error;
			this.$emit('error', error);
		},
		validateSubdomain(subdomain) {
			if (!subdomain) {
				return 'Subdomain cannot be empty';
			}
			if (subdomain.length < 5) {
				return 'Subdomain too short. Use 5 or more characters';
			}
			if (subdomain.length > 32) {
				return 'Subdomain too long. Use 32 or less characters';
			}
			if (!subdomain.match(/^[a-z0-9][a-z0-9-]*[a-z0-9]$/)) {
				return 'Subdomain contains invalid characters. Use lowercase characters, numbers and hyphens';
			}
			return null;
		}
	}
};
</script>
