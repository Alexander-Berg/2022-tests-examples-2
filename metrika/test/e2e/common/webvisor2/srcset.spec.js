const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('webvisor2', function () {
    const baseUrl = 'test/webvisor2/';
    const counterId = 123;

    it.skip('srcset captor / image srcset mutation', function () {
        return this.browser
            .deleteCookie()
            .timeoutsAsyncScript(30000)
            .url(`${baseUrl}mutation.hbs`)
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.addRule(
                            {
                                regex: `/watch/${options.counterId}`,
                                body: {
                                    settings: {
                                        webvisor: {
                                            recp: '1.0000',
                                        },
                                    },
                                },
                            },
                            function () {
                                document.cookie = '_ym_debug=""';

                                serverHelpers.collectRequestsForTime(
                                    4000,
                                    'webvisor',
                                );

                                new Ya.Metrika2({
                                    id: options.counterId,
                                    webvisor: true,
                                    childIframe: true,
                                });

                                setTimeout(() => {
                                    document.querySelector('#image').click();
                                }, 1000);
                            },
                        );
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(e2eUtils.getWebvisorData.bind(e2eUtils))
            .then((visorData) => {
                const mutations = visorData.filter(
                    ({ type }) => type === 'mutation',
                );

                const srcChanges = mutations
                    .flatMap((item) => item.data.meta.changes)
                    .flatMap((item) => (item.c ? item.c : []))
                    .map((item) => item.at.src && item.at.src.n);

                chai.expect(srcChanges[0]).to.include('secondImg');
            });
    });
});
