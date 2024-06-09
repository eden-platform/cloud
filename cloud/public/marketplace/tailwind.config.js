const config = require('../../../dashboard/tailwind.config');

module.exports = {
	presets: config.presets,
	theme: config.theme,
	plugins: config.plugins,
	content: [
		'./cloud/**/marketplace/**/*.html',
		'./cloud/**/marketplace/*.html',
		'./cloud/**/marketplace_*.html',
	],
};
