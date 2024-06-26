export default class FileUploader {
	constructor() {
		this.listeners = {};
	}

	on(event, handler) {
		this.listeners[event] = this.listeners[event] || [];
		this.listeners[event].push(handler);
	}

	trigger(event, data) {
		let handlers = this.listeners[event] || [];
		handlers.forEach(handler => {
			handler.call(this, data);
		});
	}

	upload(file, options) {
		return new Promise((resolve, reject) => {
			let xhr = new XMLHttpRequest();
			xhr.upload.addEventListener('loadstart', () => {
				this.trigger('start');
			});
			xhr.upload.addEventListener('progress', e => {
				if (e.lengthComputable) {
					this.trigger('progress', {
						uploaded: e.loaded,
						total: e.total
					});
				}
			});
			xhr.upload.addEventListener('load', () => {
				this.trigger('finish');
			});
			xhr.addEventListener('error', () => {
				this.trigger('error');
				reject();
			});
			xhr.onreadystatechange = () => {
				if (xhr.readyState == XMLHttpRequest.DONE) {
					let error;
					if (xhr.status === 200) {
						let r = null;
						try {
							r = JSON.parse(xhr.responseText);
						} catch (e) {
							r = xhr.responseText;
						}
						let out = r.message || r;
						resolve(out);
					} else if (xhr.status === 403) {
						error = JSON.parse(xhr.responseText);
					} else {
						this.failed = true;
						try {
							error = JSON.parse(xhr.responseText);
						} catch (e) {
							// pass
						}
					}
					if (error && error.exc) {
						console.error(JSON.parse(error.exc)[0]);
					}
					reject(error);
				}
			};
			xhr.open('POST', '/api/method/upload_file', true);
			xhr.setRequestHeader('Accept', 'application/json');
			if (window.csrf_token && window.csrf_token !== '{{ csrf_token }}') {
				xhr.setRequestHeader('X-Eden-CSRF-Token', window.csrf_token);
			}

			let form_data = new FormData();
			if (file) {
				form_data.append('file', file, file.name);
			}
			form_data.append('is_private', +(options.private || 0));
			form_data.append('folder', options.folder || 'Home');

			if (options.file_url) {
				form_data.append('file_url', options.file_url);
			}

			if (options.doctype && options.docname) {
				form_data.append('doctype', options.doctype);
				form_data.append('docname', options.docname);
			}

			if (options.method) {
				form_data.append('method', options.method);
			}

			if (options.type) {
				form_data.append('type', options.type);
			}

			xhr.send(form_data);
		});
	}
}
