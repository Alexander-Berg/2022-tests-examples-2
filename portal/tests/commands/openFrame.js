module.exports = async function openFrame(url = '', params = undefined) {
    if (typeof url === 'object' && params === undefined) {
        params = url;
        url = '';
    }
    let queryParams = '';
    if (params) {
        if (typeof params.expFlags === 'object') {
            params.exp_flags = Object.entries(params.expFlags).map(e => e.join('=')).join(';');
            delete params.expFlags;
        }
        if (!url.endsWith('?')) {
            queryParams = '?';
        }
        queryParams += Object.entries(params).map(e => e.join('=')).join('&');
    }
    if (!url.startsWith('/gnc/frame')) {
        url += '/gnc/frame';
    }
    await this.url(url + queryParams);

    const hasData = await this.execute(() => {
        return Boolean(window.applicationData);
    });
    if (!hasData) {
        throw new Error('openFrame: Страница не загрузилась');
    }

    await this.appendStyles();
};
