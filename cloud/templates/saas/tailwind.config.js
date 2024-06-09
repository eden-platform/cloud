const config = require('../../../dashboard/tailwind.config');

module.exports = {
	theme: config.theme,
	plugins: config.plugins,
	content: ['./cloud/**/saas/*.html', './cloud/**/saas/*.html'],
};
