(async () => {
    const yt = require('@yandex-data-ui/yt-javascript-wrapper')();
    yt.setup.setGlobalOption('proxy', 'hahn.yt.yandex-team.ru');
    await yt.v3.set({
        setup: {
            proxy: 'hahn.yt.yandex.net',
            authentication: {
                type: 'oauth',
                token: process.env.YT_OAUTH_TOKEN,
            }
        },
        parameters: {
            path: '//home/morda/mikstime/testcop/@enable_dynamic_store_read',
        },
        data: true
    }).catch(e => console.log(e));
})();
