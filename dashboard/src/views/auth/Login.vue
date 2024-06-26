<template>
	<LoginBox
		v-if="!successMessage"
		:title="!forgot ? 'Log in to your account' : 'Reset your password'"
	>
		<form class="flex flex-col" @submit.prevent="login">
			<FormControl
				label="Email"
				placeholder="johndoe@mail.com"
				v-model="email"
				name="email"
				autocomplete="email"
				:type="email !== 'Administrator' ? 'email' : 'text'"
				required
			/>
			<FormControl
				class="mt-4"
				v-if="!forgot"
				label="Password"
				type="password"
				placeholder="•••••"
				v-model="password"
				name="password"
				autocomplete="current-password"
				required
			/>
			<div class="mt-2 text-sm">
				<router-link v-if="forgot" to="/login">
					I remember my password
				</router-link>
				<router-link v-else to="/login/forgot"> Forgot Password? </router-link>
			</div>
			<ErrorMessage :message="errorMessage" class="mt-4" />
			<Button
				class="mt-4"
				:disabled="state === 'RequestStarted'"
				@click="loginOrResetPassword"
				variant="solid"
			>
				{{ !forgot ? 'Log in with email' : 'Reset Password' }}
			</Button>
			<template v-if="!forgot">
				<div class="-mb-2 mt-6 border-t text-center">
					<div class="-translate-y-1/2 transform">
						<span
							class="bg-white px-2 text-xs uppercase leading-8 tracking-wider text-gray-800"
						>
							Or
						</span>
					</div>
				</div>
			</template>
		</form>

		<div class="flex flex-col">
			<Button
				v-if="$resources.guestFeatureFlags.data?.enable_google_oauth === 1"
				@click="$resources.oauthLogin.submit()"
				:loading="$resources.oauthLogin.loading"
			>
				<div class="flex">
					<GoogleIcon />
					<span class="ml-2">Log in with Google</span>
				</div>
			</Button>
			<router-link class="mt-10 text-center text-base" to="/signup">
				Sign up for a new account
			</router-link>
		</div>
	</LoginBox>
	<div class="mx-auto mt-20 w-96 sm:ml-auto sm:mr-auto" v-else>
		<SuccessCard title="Password Reset Link Sent.">
			We have sent an email to <span class="font-semibold">{{ email }}</span
			>. Please click on the link received to reset your password.
		</SuccessCard>
	</div>
</template>
<script>
import LoginBox from '@/views/partials/LoginBox.vue';
import GoogleIcon from '@/components/icons/GoogleIcon.vue';
import { notify } from '@/utils/toast';

export default {
	name: 'Login',
	props: {
		forgot: {
			default: false
		}
	},
	components: {
		LoginBox,
		GoogleIcon
	},
	data() {
		return {
			state: null, // Idle, Logging In, Login Error
			email: null,
			password: null,
			errorMessage: null,
			successMessage: null
		};
	},
	watch: {
		forgot() {
			this.errorMessage = null;
			this.state = null;
			this.password = null;
			this.successMessage = null;
		}
	},
	resources: {
		login() {
			return {
				url: 'login',
				params: {
					usr: this.email,
					pwd: this.password
				},
				onSuccess(res) {
					if (res) {
						this.$account.fetchAccount();
						this.$auth.isLoggedIn = true;
						return res;
					}
				}
			};
		},
		oauthLogin() {
			return {
				url: 'cloud.api.oauth.google_login',
				onSuccess(r) {
					window.location = r;
				},
				onError(e) {
					this.state = null;
					notify({
						title: e,
						color: 'red',
						icon: 'x'
					});
				}
			};
		},
		guestFeatureFlags() {
			return {
				url: 'cloud.api.account.guest_feature_flags',
				auto: true
			};
		}
	},
	methods: {
		async loginOrResetPassword() {
			try {
				this.errorMessage = null;
				this.state = 'RequestStarted';
				if (!this.forgot) {
					await this.login();
				} else {
					await this.resetPassword();
				}
			} catch (error) {
				console.error(error);
				this.errorMessage = error.messages.join('\n');
			} finally {
				this.state = null;
			}
		},
		async login() {
			if (this.email && this.password) {
				await this.$auth.login(this.email, this.password);
			}
		},
		async resetPassword() {
			await this.$auth.resetPassword(this.email);
			this.successMessage = true;
		}
	}
};
</script>
