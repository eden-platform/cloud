<template>
	<Card
		title="Team Members and Permissions"
		subtitle="Team members can access your account on your behalf."
	>
		<template #actions>
			<Button
				v-if="showManageTeamButton"
				@click="showManageMemberDialog = true"
			>
				Add New Member
			</Button>
		</template>
		<div class="max-h-96 divide-y">
			<ListItem
				v-for="member in $account.team_members"
				:title="`${member.first_name} ${member.last_name}`"
				:description="member.name"
				:key="member.name"
			>
				<template #actions>
					<Badge
						label="Owner"
						color="blue"
						class="ml-2"
						v-if="member.name == $account.team.user"
					/>
					<Dropdown v-else :options="dropdownItems(member)" right>
						<template v-slot="{ open }">
							<Button icon="more-horizontal" />
						</template>
					</Dropdown>
				</template>
			</ListItem>
		</div>

		<Dialog
			:options="{
				title: 'Add New Member',
				actions: [
					{
						label: 'Send Invitation',
						variant: 'solid',
						loading: $resources.addMember.loading,
						onClick: () => $resources.addMember.submit({ email: memberEmail })
					}
				]
			}"
			v-model="showManageMemberDialog"
		>
			<template v-slot:body-content>
				<FormControl
					label="Enter the email address of your teammate to invite them."
					class="mt-2"
					v-model="memberEmail"
					required
				/>
				<ErrorMessage :message="$resources.addMember.error" />
			</template>
		</Dialog>
		<EditPermissions
			:type="'user'"
			:show="showEditMemberDialog"
			:name="memberName"
			@close="showEditMemberDialog = false"
		/>
	</Card>
</template>
<script>
import EditPermissions from './EditPermissions.vue';
import { notify } from '@/utils/toast';

export default {
	name: 'AccountMembers',
	components: {
		EditPermissions
	},
	data() {
		return {
			showManageMemberDialog: false,
			showEditMemberDialog: false,
			memberName: '',
			showAddMemberForm: false,
			memberEmail: null
		};
	},
	resources: {
		addMember: {
			url: 'cloud.api.account.add_team_member',
			onSuccess() {
				this.showManageMemberDialog = false;
				this.memberEmail = null;
				notify({
					title: 'Invite Sent!',
					message: 'They will receive an email shortly to join your team.',
					color: 'green',
					icon: 'check'
				});
			}
		},
		removeMember: {
			url: 'cloud.api.account.remove_team_member',
			onSuccess() {
				this.showManageMemberDialog = false;
				this.$account.fetchAccount();
				notify({
					title: 'Team member removed.',
					icon: 'check',
					color: 'green'
				});
			}
		}
	},
	methods: {
		getRoleBadgeProps(member) {
			let role = 'Member';
			if (this.$account.team.name == member.name) {
				role = 'Owner';
			}

			return {
				status: role,
				color: {
					Owner: 'blue',
					Member: 'gray'
				}[role]
			};
		},
		removeMember(member) {
			this.$confirm({
				title: 'Remove Member',
				message: `Are you sure you want to remove ${member.first_name} ?`,
				actionLabel: 'Remove',
				actionColor: 'red',
				action: closeDialog => {
					this.$resources.removeMember.submit({ user_email: member.name });
					closeDialog();
				}
			});
		},
		dropdownItems(member) {
			return [
				{
					label: 'Edit Permissions',
					icon: 'edit',
					onClick: () => {
						this.memberName = member.name;
						this.showEditMemberDialog = true;
					}
				},
				{
					label: 'Remove',
					icon: 'trash-2',
					onClick: () => this.removeMember(member)
				}
			];
		}
	},
	computed: {
		showManageTeamButton() {
			const team = this.$account.team;
			let show = this.$account.hasRole('Press Admin');
			return (
				show &&
				(team.default_payment_method ||
					team.payment_mode == 'Prepaid Credits' ||
					team.free_account ||
					team.erpnext_partner ||
					team.parent_team)
			);
		}
	}
};
</script>
