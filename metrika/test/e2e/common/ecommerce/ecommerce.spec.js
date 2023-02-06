const chai = require('chai');
const e2eUtils = require('../../utils/index.js');

describe('Ecommerce e2e test', function () {
    const baseUrl = 'test/ecommerce/ecommerce.hbs';
    const fullUrl = `${e2eUtils.baseUrl}/${baseUrl}`;
    const counterId = 26302566;

    const ecommerceStub = {
        id: '3002',
        affiliation: 'Supplier 1',
        revenue: 7,
        shipping: 7,
        tax: 3,
        currency: 'CAD',
        goods: [
            {
                id: 'ug_0026',
                name: 'box of something',
                SKU: 'AB123',
                category: 'some category/some sub category',
                price: 1.5,
                brand: 'The Box',
                variant: 'gray',
                quantity: 2,
            },
            {
                id: 'ug_0027',
                name: 'box of something other',
                SKU: 'AB124',
                category: 'some category/some sub category',
                price: 2.5,
                brand: 'The Box',
                variant: 'gray',
                quantity: 3,
                coupon: 'GOODS_COUPON',
            },
        ],
    };

    beforeEach(function () {
        return this.browser.timeoutsAsyncScript(10000).deleteCookie();
    });

    it('should exists ecommerce methods', function () {
        return this.browser
            .url(baseUrl)
            .getText('body')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options, done) {
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                        });
                        done(counter);
                    },
                    counterId,
                }),
            )
            .then(({ value: counter }) => {
                chai.expect(counter).to.include.any.keys('ecommerceAdd');
                chai.expect(counter).to.include.any.keys('ecommerceRemove');
                chai.expect(counter).to.include.any.keys('ecommerceDetail');
                chai.expect(counter).to.include.any.keys('ecommercePurchase');
            });
    });

    it('should send valid data', function () {
        return this.browser
            .url(baseUrl)
            .getText('body')
            .then(
                e2eUtils.provideServerHelpers(this.browser, {
                    cb(serverHelpers, options) {
                        serverHelpers.collectRequests(300);
                        const counter = new Ya.Metrika2({
                            id: options.counterId,
                            ecommerce: 'testDataLayer',
                        });

                        counter.ecommerceAdd(options.ecommerceStub);
                        counter.ecommerceRemove(options.ecommerceStub);
                        counter.ecommerceDetail(options.ecommerceStub);
                        counter.ecommercePurchase(options.ecommerceStub);
                    },
                    counterId,
                    ecommerceStub,
                }),
            )
            .then(e2eUtils.handleRequest(this.browser))
            .then(({ value: allRequests }) => {
                const parseData = {};

                allRequests
                    .map(e2eUtils.getRequestParams)
                    .filter(({ brInfo: { pa } }) => pa)
                    .forEach((req) => {
                        chai.expect(req.params['page-url']).to.be.equal(
                            fullUrl,
                        );
                        const [ecommerceData] = req.siteInfo.__ym.ecommerce;
                        const event = Object.keys(ecommerceData)[0];
                        const actionField = ecommerceData[event]?.actionField;
                        const products = ecommerceData[event]?.products;
                        const currencyCode = ecommerceData?.currencyCode;

                        chai.expect(actionField.id).to.be.equal('3002');
                        chai.expect(actionField.affiliation).to.be.equal(
                            'Supplier 1',
                        );
                        chai.expect(actionField.revenue).to.be.equal(7);
                        chai.expect(actionField.shipping).to.be.equal(7);
                        chai.expect(actionField.tax).to.be.equal(3);
                        chai.expect(products.length).to.equal(2);
                        chai.expect(currencyCode).to.be.equal('CAD');

                        parseData[event] = ecommerceData;
                    });

                chai.expect(parseData).to.include.any.keys('add');
                chai.expect(parseData).to.include.any.keys('remove');
                chai.expect(parseData).to.include.any.keys('detail');
                chai.expect(parseData).to.include.any.keys('purchase');
            });
    });
});
