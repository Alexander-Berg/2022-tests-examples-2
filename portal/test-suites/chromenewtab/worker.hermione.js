'use strict';

specs('service-worker', function () {
    const {updateScenario} = require('../../scenarios/service-worker-update');
    this.timeout(120000);
    it('Воркер корректно обновлятся', function () {
        return updateScenario.call(this, {
            page: '/chrome/newtab',
            scope: '/chrome/',
            worker: 'white/_newtab3.js',
            /* В продакшне меняется location, если апи нтп не доступно,
             * поэтому не меняем страницу на прод
             */
            replacePageInCache: false
        });
    });

    describe('установка воркера', function () {
        const CACHE_BASE = 'home-chromenewtab3-';
        const {
            getCacheVersion,
            getCachesKeys,
            getCacheUrls,
            deleteCacheContent,
            shouldHaveFiles
        } = require('../../commands/util/cacheUtils');

        function checkCacheFiles(items) {
            items.should.be.an('array');
            items.length.should.not.equal(0);
            shouldHaveFiles(items, /chrome\/newtab/, 1, 'страница');
            shouldHaveFiles(items, /(\/tmpl\/white\/|\/tmpl\/freeze\/|yastatic\.net\/s3\/home-(?:beta|static)).*\.css$/, 2, 'css файл страницы');
            shouldHaveFiles(items, /(\/tmpl\/white\/|\/tmpl\/freeze\/|yastatic\.net\/s3\/home-(?:beta|static)).*\.js$/, 1, 'js файл страницы');
            shouldHaveFiles(items, /yastatic\.net\/.*jquery.min.js$/, 1, 'jquery');
        }

        beforeEach('Удаление кэша', async function() {
            await this.browser.yaOpenMorda({
                dump: true
            });

            const version = await getCacheVersion.call(this);
            await deleteCacheContent.call(this, CACHE_BASE, version);
        });

        it('устанавливается, наполняет кеш', async function() {
            await this.browser.yaOpenMorda({path: '/chrome/newtab'});
            await this.browser.yaWaitForActiveWorker();
            const {keys, version} = await getCachesKeys.call(this);

            version.should.exist;
            keys.should.be.an('array')
                .and.include(CACHE_BASE + version)
                .and.have.lengthOf(1);

            const items = await getCacheUrls.call(this, CACHE_BASE);

            checkCacheFiles(items);
        });

        /* На девинстансах не работает преобразование no-cors -> cors, т.к. в регуларке зашита ястатика */
        it.skip('дополняет кеш при запросе файла', async function() {
            await this.browser.yaOpenMorda({path: '/chrome/newtab'});
            await this.browser.yaWaitForActiveWorker();
            await deleteCacheContent.call(this, CACHE_BASE);
            await this.browser.yaReload();
            const items = await getCacheUrls.call(this, CACHE_BASE);

            checkCacheFiles(items);
        });
    });
});
