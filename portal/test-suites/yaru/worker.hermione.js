'use strict';

const {
    getCachesKeys,
    getCacheUrls,
    deleteCacheContent,
    shouldHaveFiles
} = require('../../commands/util/cacheUtils');

specs('worker', function () {
    const CACHE_BASE = 'home-yaru-';
    describe.skip('установка воркера', function () {
        it('устанавливается, наполняет кеш', async function () {
            await this.browser.yaOpenMorda({yaru: true});

            await this.browser.yaWaitForActiveWorker();
            const {keys, version} = await getCachesKeys.call(this);

            version.should.exist;
            keys.should.be.an('array')
                .and.include(CACHE_BASE + version)
                .and.have.lengthOf(1);

            const items = await getCacheUrls.call(this, CACHE_BASE);

            shouldHaveFiles(items, /\//, 1, 'страница');
            shouldHaveFiles(items, /(\/tmpl\/white\/|\/tmpl\/freeze\/|yastatic\.net\/s3\/home-(?:beta|static)).*\.js$/, 1, 'js файл страницы');
        });

        it('дополняет кеш при запросе файла', async function () {
            await this.browser.yaOpenMorda({yaru: true});
            await this.browser.yaWaitForActiveWorker();

            await deleteCacheContent.call(this, CACHE_BASE);

            await this.browser.yaReload();

            const items = await getCacheUrls.call(this, CACHE_BASE);

            shouldHaveFiles(items, /\//, 1, 'страница');
            shouldHaveFiles(items, /(\/tmpl\/white\/|\/tmpl\/freeze\/|yastatic\.net\/s3\/home-(?:beta|static)).*\.js$/, 1, 'js файл страницы');
        });
    });
});
