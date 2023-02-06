const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('DataLayer e2e test', function () {
    const baseUrl = 'test/dataLayer/dataLayer.hbs';
    const fullUrl = `${e2eUtils.baseUrl}/${baseUrl}`;
    const getEcommerceRequests = (rawRequests) =>
        rawRequests
            .map(e2eUtils.getRequestParams)
            .filter(({ brInfo: { pa } }) => pa)
            .map((req) => {
                chai.expect(req.params['page-url']).to.eq(fullUrl);
                return req.siteInfo.__ym.ecommerce;
            })
            .filter(Boolean);
    let opt = {};

    beforeEach(function () {
        opt = {
            counterId: 26302566,
            addEvent: { ecommerce: { add: 1 } },
            purchaseEvent: { ecommerce: { purchase: 1 } },
            deleteEvent: { ecommerce: { delete: 1 } },
            removeEvent: { ecommerce: { remove: 1 } },
            detailEvent: { ecommerce: { detail: 1 } },
            invalidEvent: { ecommerce: { suspect: 1 } },
            dataLayerName: 'testVar',
            defaultDataLayer: 'dataLayer',
        };
        return this.browser
            .deleteCookie()
            .timeoutsAsyncScript(10000)
            .url(baseUrl)
            .getText('body')
            .then((innerText) => {
                chai.expect(innerText).to.be.equal('DataLayer page');
            });
    });
    it('send data from google gtag dataLayer (and uses default)', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        new Ya.Metrika2({
                            id: options.counterId,
                            ecommerce: true,
                        });
                        window[options.defaultDataLayer] = [
                            [
                                'event',
                                'add_to_cart',
                                {
                                    items: [
                                        {
                                            id: 'addItem',
                                        },
                                    ],
                                },
                            ],
                        ];
                        const dataLayer = window[options.defaultDataLayer];
                        dataLayer.push([
                            'event',
                            'view_item',
                            {
                                items: [
                                    {
                                        id: 'viewItem',
                                        someField: 'someVal',
                                    },
                                ],
                            },
                        ]);
                        dataLayer.push([
                            'event',
                            'purchase',
                            {
                                transaction_id: 'purchaseId',
                                currency: 'RUB',
                                value: 1111,
                                items: [
                                    {
                                        id: 'purchaseItem',
                                    },
                                ],
                            },
                        ]);
                        // GA4 format
                        dataLayer.push({
                            event: 'remove_from_cart',
                            ecommerce: {
                                items: [
                                    {
                                        item_id: 'removeItem',
                                    },
                                ],
                            },
                        });
                        serverHelpers.collectRequests(2000);
                    },
                    ...opt,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: allRequests }) => {
                const checks = {
                    add: (event) => {
                        chai.expect(event.add.products[0].id).to.be.equal(
                            'addItem',
                        );
                    },
                    remove: (event) => {
                        chai.expect(event.remove.products[0].id).to.be.equal(
                            'removeItem',
                        );
                    },
                    detail: (event) => {
                        const [product] = event.detail.products;
                        chai.expect(product.id).to.be.equal('viewItem');
                        chai.expect(product.someField).to.be.equal('someVal');
                    },
                    'purchase,currencyCode': (event) => {
                        chai.expect(event.purchase.products[0].id).to.be.equal(
                            'purchaseItem',
                        );
                        chai.expect(event.purchase.actionField.id).to.be.equal(
                            'purchaseId',
                        );
                        chai.expect(
                            event.purchase.actionField.revenue,
                        ).to.be.equal(1111);
                        chai.expect(event.currencyCode).to.be.equal('RUB');
                    },
                };
                const ecommerceRequests = getEcommerceRequests(allRequests);
                chai.expect(ecommerceRequests).to.be.not.empty;
                ecommerceRequests.forEach((ecom) => {
                    const event = ecom
                        .map((e) => {
                            const keys = Object.keys(e).join();
                            if (checks[keys]) {
                                checks[keys](e);
                            }
                            return keys;
                        })
                        .join();
                    chai.expect([
                        'add',
                        'detail',
                        'remove',
                        'purchase,currencyCode',
                    ]).to.include(event);
                });
            });
    });
    it('send data from dataLayer before counter was inited', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        window[options.dataLayerName] = [
                            options.detailEvent,
                            options.deleteEvent,
                            options.purchaseEvent,
                            options.invalidEvent,
                        ];
                        const dataLayer = window[options.dataLayerName];
                        new Ya.Metrika2({
                            id: options.counterId,
                            ecommerce: options.dataLayerName,
                        });
                        dataLayer.push(options.removeEvent);
                        serverHelpers.collectRequests(2000);
                    },
                    ...opt,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: allRequests }) => {
                const ecommerceRequests = getEcommerceRequests(allRequests);
                chai.expect(ecommerceRequests).to.be.not.empty;
                ecommerceRequests.forEach((ecom) => {
                    const event = ecom.map((e) => Object.keys(e).join()).join();
                    chai.expect([
                        'purchase',
                        'remove',
                        'detail',
                        'delete',
                    ]).to.include(event);
                });
            });
    });
    it('send data from dataLayer after counter was inited', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        new Ya.Metrika2({
                            id: options.counterId,
                            ecommerce: options.dataLayerName,
                        });

                        window[options.dataLayerName] = [
                            options.addEvent,
                            options.removeEvent,
                        ];
                        const dataLayer = window[options.dataLayerName];
                        dataLayer.push(options.removeEvent);
                        serverHelpers.collectRequests(2000);
                    },
                    ...opt,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: allRequests }) => {
                const ecommerceRequests = getEcommerceRequests(allRequests);
                chai.expect(ecommerceRequests).to.be.not.empty;
                ecommerceRequests.forEach((ecom) => {
                    const event = ecom.map((e) => Object.keys(e).join()).join();
                    chai.expect(['remove', 'add']).to.include(event);
                });
            });
    });

    it('should work if data is array-like but not array', function () {
        const purchaseItem = {
            id: Math.random().toString().slice(2),
            name: 'test',
        };
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        function createArguments() {
                            // eslint-disable-next-line prefer-rest-params
                            return arguments;
                        }

                        new Ya.Metrika2({
                            id: options.counterId,
                            ecommerce: options.dataLayerName,
                        });

                        const dataLayer = [];
                        window[options.dataLayerName] = dataLayer;

                        serverHelpers.collectRequests(2000);
                        setTimeout(() => {
                            dataLayer.push(
                                createArguments('event', 'purchase', {
                                    items: [options.purchaseItem],
                                }),
                            );
                        });
                    },
                    counterId: opt.counterId,
                    dataLayerName: opt.dataLayerName,
                    purchaseItem,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: allRequests }) => {
                const ecommerceRequests = getEcommerceRequests(allRequests);
                chai.expect(
                    ecommerceRequests,
                    'Wrong amount of ecommerce requests',
                ).to.have.lengthOf(1);
                ecommerceRequests.forEach(([ecommerceEvent]) => {
                    chai.expect(ecommerceEvent).to.have.key('purchase');
                    chai.expect(
                        ecommerceEvent.purchase.products,
                        'Wrong amount of ecommerce products',
                    ).to.have.lengthOf(1);
                    const [item] = ecommerceEvent.purchase.products;
                    chai.expect(item).to.deep.eq(purchaseItem);
                });
            });
    });
    it('ecommerce should not fail if no data provided', function () {
        return this.browser
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        new Ya.Metrika2({
                            id: options.counterId,
                            ecommerce: options.dataLayerName,
                        });

                        const dataLayer = [];
                        window[options.dataLayerName] = dataLayer;

                        serverHelpers.collectRequests(2000);
                        setTimeout(() => {
                            dataLayer.push(['event', 'purchase']);
                            dataLayer.push(['event', 'purchase', null]);
                            dataLayer.push({
                                ecommerce: {},
                            });
                            dataLayer.push({
                                event: 'purchase',
                            });
                        });
                    },
                    counterId: opt.counterId,
                    dataLayerName: opt.dataLayerName,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: allRequests }) => {
                const ecommerceRequests = getEcommerceRequests(allRequests);
                chai.expect(ecommerceRequests).to.be.empty;
            });
    });
});
