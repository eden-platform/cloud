<script setup>
import { reactive } from 'vue';
import { createResource } from 'frappe-ui';
import StarRatingInput from '@/components/StarRatingInput.vue';
import { getDocResource } from '../../utils/resource';
import { DashboardError } from '../../utils/error';

const props = defineProps({
	marketplaceApp: String
});
const app = getDocResource({
	doctype: 'Marketplace App',
	name: props.marketplaceApp
});
const review = reactive({
	app: props.marketplaceApp,
	title: '',
	rating: 5,
	review: ''
});
const submitReview = createResource({
	url: 'press.api.marketplace.submit_user_review',
	validate() {
		if (!review.title) {
			throw new DashboardError('Please add a title to your review');
		}
		if (!review.review) {
			throw new DashboardError('Review cannot be empty');
		}
	},
	onSuccess() {
		window.location.href = `/marketplace/apps/${props.marketplaceApp}`;
	}
});
</script>

<template>
	<div class="mx-auto mt-12 max-w-xl px-5 text-base sm:px-8">
		<div class="mb-4 flex items-center space-x-4">
			<img
				:src="app?.doc.image"
				class="h-12 w-12 rounded-lg border"
				:alt="app?.doc.name"
			/>
			<h1 class="text-xl font-semibold">{{ app?.doc.title }}</h1>
		</div>
		<div>
			<div class="mb-3">
				<span class="mb-2 block text-sm leading-4 text-gray-700"> Rating </span>
				<StarRatingInput v-model="review.rating" />
			</div>
			<FormControl
				class="mb-3"
				v-model="review.title"
				label="Title"
				placeholder="Review Title"
			/>
			<FormControl
				v-model="review.review"
				type="textarea"
				label="Review this product"
				placeholder="Write Review"
			/>
			<ErrorMessage class="mt-2" :message="submitReview.error" />
			<Button
				class="mt-4 w-full"
				:loading="submitReview.loading"
				variant="solid"
				@click="submitReview.submit({ ...review })"
				>Submit</Button
			>
		</div>
	</div>
</template>
