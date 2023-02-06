const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('External and download links', function () {
    const pathToTestPage = 'test/externalLinks/externalLinks.hbs';
    const testUrl = `${e2eUtils.baseUrl}/${pathToTestPage}`;

    const counterId = 26302566;
    const firstCounterId = 1;
    const secondCounterId = 2;

    const validateRequest = (
        { params = {}, brInfo = {}, counterId: realId },
        id = null,
        pageUrl,
        referrer,
        title,
        isDownload,
        isExtLink,
    ) => {
        return [
            params['page-url'] === pageUrl,
            params['page-ref'] === referrer,
            brInfo.t === title,
            isDownload ? brInfo.dl === '1' : brInfo.dl === undefined,
            isExtLink ? brInfo.ln === '1' : brInfo.ln === undefined,
            id ? id === realId : true,
        ].every((val) => val);
    };

    const hasRequest = (
        requests,
        pageUrl,
        referrer,
        title,
        isDownload = false,
        isExtLink = false,
    ) => {
        let isDuplicate = false;
        const hasRequestResult = requests.reduce((found, request) => {
            const parsedRequest = e2eUtils.getRequestParams(request);
            const result = validateRequest(
                parsedRequest,
                null,
                pageUrl,
                referrer,
                title,
                isDownload,
                isExtLink,
            );

            if (found && result) {
                isDuplicate = true;
            }

            return found || result;
        }, false);

        if (isDuplicate) {
            return false;
        }

        return hasRequestResult;
    };

    beforeEach(function () {
        return this.browser
            .deleteCookie()
            .timeoutsAsyncScript(10000)
            .url(testUrl);
    });

    it('Handles external links and ignores internal link', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(
                            1000,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );
                        new Ya.Metrika2({
                            id: options.counterId,
                            trackLinks: true,
                        });

                        document.querySelector('#ext-link').click();
                        document.querySelector('#int-link').click();
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const hasExternalLinkRequest = hasRequest(
                    requests,
                    'https://myrandomsitehost.ru/some-url',
                    testUrl,
                    'External link',
                    false,
                    true,
                );
                const hasInternalLinkRequest = hasRequest(
                    requests,
                    `${e2eUtils.baseUrl}/internal-link`,
                    testUrl,
                    'Internal link',
                );

                chai.expect(hasExternalLinkRequest, 'External link click').to.be
                    .true;
                chai.expect(hasInternalLinkRequest, 'Internal link click').to.be
                    .false;
            });
    });

    it('Handles files download links including user extension', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(
                            2000,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );

                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                            trackLinks: true,
                        });

                        document
                            .querySelector('#file-with-user-extension-link')
                            .click();
                        counter.addFileExtension('zhopeg');
                        document.querySelector('#file-link').click();
                        document.querySelector('#file-ext-link').click();
                        document
                            .querySelector('#file-with-user-extension-link')
                            .click();
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const hasInternalFileDownload = hasRequest(
                    requests,
                    `${e2eUtils.baseUrl}/files/file.txt`,
                    testUrl,
                    'File',
                    true,
                );
                const hasExternalFileDownload = hasRequest(
                    requests,
                    'https://myrandomsitehost.ru/some-url/file.txt',
                    testUrl,
                    'External file',
                    true,
                    true,
                );
                const hasUserExtensionFileDownload = hasRequest(
                    requests,
                    `${e2eUtils.baseUrl}/files/file.zhopeg`,
                    testUrl,
                    'Strange file',
                    true,
                    false,
                );

                chai.expect(hasInternalFileDownload, 'internal file download')
                    .to.be.true;
                chai.expect(hasExternalFileDownload, 'External file download')
                    .to.be.true;
                chai.expect(
                    hasUserExtensionFileDownload,
                    'User extension file click',
                ).to.be.true;
            });
    });

    it('Handles links with custom protocols like tel: or mailto:', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(
                            1000,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );
                        new Ya.Metrika2({
                            id: options.counterId,
                            trackLinks: true,
                        });

                        document.querySelector('#tel-link').click();
                        document.querySelector('#mailto-link').click();
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const hasTelLinkRequest = hasRequest(
                    requests,
                    'tel:+79999999999',
                    testUrl,
                    'Tel',
                    false,
                    true,
                );
                const hasMailtoLinkRequest = hasRequest(
                    requests,
                    'mailto:metrica-dev@yandex-team.ru',
                    testUrl,
                    'Mailto',
                    false,
                    true,
                );

                chai.expect(hasTelLinkRequest, 'tel: link click').to.be.true;
                chai.expect(hasMailtoLinkRequest, 'mailto: link click').to.be
                    .true;
            });
    });

    it('Handles extLink method call', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                            trackLinks: true,
                        });

                        serverHelpers.collectRequests(
                            2000,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );

                        counter.extLink('http://randomdomain.com', {
                            title: 'Random link click',
                        });
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const hasExtLinkClick = hasRequest(
                    requests,
                    'http://randomdomain.com',
                    testUrl,
                    'Random link click',
                    false,
                    true,
                );

                chai.expect(hasExtLinkClick, 'extLink click').to.be.true;
            });
    });

    it('Handles file method call', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(
                            2000,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );

                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                            trackLinks: true,
                        });

                        counter.file();

                        counter.file('http://randomdomain.com', {
                            title: 'Random link click',
                        });
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const hasFileLinkClick = hasRequest(
                    requests,
                    'http://randomdomain.com',
                    testUrl,
                    'Random link click',
                    true,
                    true,
                );

                chai.expect(hasFileLinkClick, 'file method').to.be.true;
            });
    });

    it(`Handles method's calls without options`, function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(
                            1000,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );

                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });

                        counter.extLink('http://randomdomain.com');
                        counter.file('http://randomdomain.com');
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const title = 'external link page title';
                const hasExtLinkCall = hasRequest(
                    requests,
                    'http://randomdomain.com',
                    testUrl,
                    title,
                    false,
                    true,
                );
                const hasFileLinkCall = hasRequest(
                    requests,
                    'http://randomdomain.com',
                    testUrl,
                    title,
                    true,
                    true,
                );

                chai.expect(hasExtLinkCall, 'extLink method').to.be.true;
                chai.expect(hasFileLinkCall, 'file method').to.be.true;
            });
    });

    it(`Handles custom protocols in extLink method call`, function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(
                            1000,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );

                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });

                        counter.extLink('tel:+79999999999', {
                            title: 'random',
                        });
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: requests }) => {
                const hasExtLinkCall = hasRequest(
                    requests,
                    'tel:+79999999999',
                    testUrl,
                    'random',
                    false,
                    true,
                );

                chai.expect(hasExtLinkCall, 'extLink method').to.be.true;
            });
    });

    it(`doesn't log callback's error`, function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(
                            1000,
                            (requests, done) => {
                                done({
                                    requests,
                                    errors: getPageErrors(),
                                });
                            },
                            options.regexp.defaultRequestRegEx,
                        );
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                            trackLinks: true,
                        });

                        counter.extLink('http://randomdomain.com', {
                            callback() {
                                throw new Error('user error');
                            },
                        });
                        counter.file('http://randomdomain.com', {
                            callback() {
                                throw new Error('user error');
                            },
                        });
                    },
                    counterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value }) => {
                chai.expect(value.requests.length).to.be.equal(3);
                chai.expect(value.errors.usual.length).to.be.equal(2);
                chai.expect(value.errors.unhandledrejection.length).to.be.equal(
                    0,
                );

                value.errors.usual.forEach((usualError) => {
                    chai.expect(usualError).to.include('user error');
                });
            });
    });

    it('Gets disabled if trackLinks flag is false', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(
                            2000,
                            null,
                            options.regexp.defaultRequestRegEx,
                        );
                        const firstCounter = new Ya.Metrika2({
                            id: options.firstCounterId,
                            trackLinks: false,
                        });
                        const secondCounter = new Ya.Metrika2({
                            id: options.secondCounterId,
                            trackLinks: true,
                        });
                        document.querySelector('#file-ext-link').click();
                        firstCounter.trackLinks({});
                        secondCounter.trackLinks(false);
                        document.querySelector('#ext-link').click();
                    },
                    firstCounterId,
                    secondCounterId,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: rawRequests }) => {
                let firstRequestReceived = false;
                let secondRequestReceived = false;
                const parsedRequests = rawRequests.map(
                    e2eUtils.getRequestParams,
                );
                chai.expect(
                    parsedRequests.length,
                    'not all requests arrived',
                ).to.be.above(3);
                parsedRequests.forEach((request) => {
                    if (!firstRequestReceived) {
                        firstRequestReceived = validateRequest(
                            request,
                            '1',
                            'https://myrandomsitehost.ru/some-url',
                            testUrl,
                            'External link',
                            false,
                            true,
                        );
                    }
                    if (!secondRequestReceived) {
                        secondRequestReceived = validateRequest(
                            request,
                            '2',
                            'https://myrandomsitehost.ru/some-url/file.txt',
                            testUrl,
                            'External file',
                            true,
                            true,
                        );
                    }
                });
                chai.expect(firstRequestReceived, 'first request').to.be.true;
                chai.expect(secondRequestReceived, 'second request').to.be.true;
            });
    });
});
