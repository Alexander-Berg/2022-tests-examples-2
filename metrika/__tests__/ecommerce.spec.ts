import * as chai from 'chai';
import * as sinon from 'sinon';
import * as counter from '@src/utils/counter';
import * as dataL from '@src/utils/dataLayerObserver';
import * as defer from '@src/utils/defer';
import * as numberUtils from '@src/utils/number';
import * as counterSettingsUtils from '@src/utils/counterSettings';
import { ecommerce } from '@src/providers/ecommerce';
import { METHOD_NAME_PARAMS } from '@src/providers/params/const';
import {
    ECOMMERCE_ACTION_FIELD,
    ECOMMERCE_CURRENCY,
    ECOMMERCE_PRODUCTS,
} from '../const';

describe('ecommerce', () => {
    const dataLayerName = 'dl';
    const timeoutId = 123;
    let setDeferStub: sinon.SinonStub<any, any>;
    let clearDeferStub: sinon.SinonStub<any, any>;
    let dataLayerObserverStub: sinon.SinonStub<any, any>;
    let getCounterStub: sinon.SinonStub<any, any>;
    let counterSettings: any = {};

    const sandbox = sinon.createSandbox();
    beforeEach(() => {
        getCounterStub = sandbox.stub(counter, 'getCounterInstance');
        sandbox.stub(numberUtils, 'isNumber').returns(true);
        setDeferStub = sandbox.stub(defer, 'setDefer').returns(timeoutId);
        clearDeferStub = sandbox.stub(defer, 'clearDefer');
        dataLayerObserverStub = sandbox.stub(dataL, 'dataLayerObserver');
        sandbox
            .stub(counterSettingsUtils, 'getCounterSettings')
            .callsFake((_, __, callback: Function) => {
                callback(counterSettings);
                return Promise.resolve();
            });
    });

    afterEach(() => {
        sandbox.restore();
    });

    it("isn't called if counter instance is undefined or ecommerce is off", () => {
        const ctx: any = {};
        let counterOptions: any = {
            ecommerce: dataLayerName,
        };
        getCounterStub.returns(null);
        ecommerce(ctx, counterOptions);
        sinon.assert.notCalled(dataLayerObserverStub);
        sinon.stub();

        counterOptions = {};
        getCounterStub.returns({ [METHOD_NAME_PARAMS]: () => {} });
        ecommerce(ctx, counterOptions);
        sinon.assert.notCalled(dataLayerObserverStub);
    });

    it('waits for dataLayer to init and sends old eocmmerce', () => {
        const ctx: any = {
            [dataLayerName]: {},
        };
        const observer = {
            on: sandbox.stub(),
        };
        counterSettings = {
            settings: {
                ecommerce: dataLayerName,
            },
        };
        const paramsStub = sandbox.stub();
        getCounterStub.returns({
            [METHOD_NAME_PARAMS]: paramsStub,
        } as any);
        dataLayerObserverStub.returns(null);

        ecommerce(ctx, {} as any);
        let [dLctx, dl] = dataLayerObserverStub.getCall(0).args;
        chai.expect(dLctx).to.equal(ctx);
        chai.expect(dl).to.equal(ctx[dataLayerName]);

        const [timeoutCtx, deferCallback, timeout] =
            setDeferStub.getCall(0).args;
        chai.expect(timeoutCtx).to.equal(ctx);
        chai.expect(timeout).to.equal(1000);
        dataLayerObserverStub.returns({ observer });

        deferCallback();
        chai.expect(clearDeferStub.calledWith(timeoutId));
        let callback: any;
        // eslint-disable-next-line prefer-const
        [dLctx, dl, callback] = dataLayerObserverStub.getCall(0).args;
        chai.expect(dLctx).to.equal(ctx);
        chai.expect(dl).to.equal(ctx[dataLayerName]);
        callback({ observer });

        const [emitterCb] = observer.on.getCall(0).args;

        emitterCb({
            ecommerce: {
                [ECOMMERCE_CURRENCY]: 123,
            },
        });
        const [params] = paramsStub.getCall(0).args;
        chai.expect(params).to.deep.equal({
            __ym: {
                ecommerce: [
                    {
                        [ECOMMERCE_CURRENCY]: 123,
                    },
                ],
            },
        });
    });

    it('inits and sends new ecommerce events', () => {
        const ctx: any = {
            [dataLayerName]: {},
        };
        const observer = {
            on: sandbox.stub(),
        };
        counterSettings = {
            settings: {
                ecommerce: dataLayerName,
            },
        };
        const paramsStub = sandbox.stub();
        getCounterStub.returns({
            [METHOD_NAME_PARAMS]: paramsStub,
        } as any);
        dataLayerObserverStub.returns({ observer });
        ecommerce(ctx, {} as any);
        const [dLctx, dl, callback] = dataLayerObserverStub.getCall(0).args;
        chai.expect(dLctx).to.equal(ctx);
        chai.expect(dl).to.equal(ctx[dataLayerName]);
        callback({ observer });
        const [emitterCb] = observer.on.getCall(0).args;

        const product = {
            id: 'P12345',
            name: 'Android Warhol T-Shirt',
            listName: 'Search Results',
            brand: 'Google',
            category: 'Apparel/T-Shirts',
            variant: 'Black',
            listPosition: 1,
            quantity: 2,
            price: '2.0',
        };
        emitterCb([
            'event',
            'view_item',
            {
                ['transaction_id']: 123,
                someRandom: 1234,
                currency: 1,
                items: [product],
            },
        ]);
        const [params] = paramsStub.getCall(0).args;

        chai.expect(params).to.deep.equal({
            __ym: {
                ecommerce: [
                    {
                        detail: {
                            [ECOMMERCE_PRODUCTS]: [product],
                            [ECOMMERCE_ACTION_FIELD]: {
                                id: 123,
                                someRandom: 1234,
                            },
                        },
                        [ECOMMERCE_CURRENCY]: 1,
                    },
                ],
            },
        });
    });

    it('inits and sends G4 ecommerce events (including puchase)', () => {
        const ctx: any = {
            [dataLayerName]: {},
        };
        const observer = {
            on: sandbox.stub(),
        };
        counterSettings = {
            settings: {
                ecommerce: dataLayerName,
            },
        };
        const paramsStub = sandbox.stub();
        getCounterStub.returns({
            [METHOD_NAME_PARAMS]: paramsStub,
        } as any);
        dataLayerObserverStub.returns({ observer });
        ecommerce(ctx, {} as any);
        const [dLctx, dl, callback] = dataLayerObserverStub.getCall(0).args;
        chai.expect(dLctx).to.equal(ctx);
        chai.expect(dl).to.equal(ctx[dataLayerName]);
        callback({ observer });
        const [emitterCb] = observer.on.getCall(0).args;

        const normalizeGoogleProduct = (product: any) => {
            const fieldsRename = {
                item_name: 'name',
                item_id: 'id',
                item_brand: 'brand',
                item_variant: 'variant',
                promotion_id: 'promotion_id',
                promotion_name: 'coupon',
                creative_name: 'creative_name',
                creative_slot: 'creative_slot',
                location_id: 'location_id',
                index: 'position',
                quantity: 'quantity',
                price: 'price',
                item_price: 'item_price',
                item_coupon: 'item_coupon',
            };
            const normalized: any = {};

            Object.entries(fieldsRename).forEach(([key, renamedKey]) => {
                if (product[key]) {
                    normalized[renamedKey] = product[key];
                }
            });
            const {
                // eslint-disable-next-line camelcase
                item_category,
                // eslint-disable-next-line camelcase
                item_category2,
                // eslint-disable-next-line camelcase
                item_category3,
                // eslint-disable-next-line camelcase
                item_category4,
            } = product;
            normalized.category = [
                // eslint-disable-next-line camelcase
                item_category,
                // eslint-disable-next-line camelcase
                item_category2,
                // eslint-disable-next-line camelcase
                item_category3,
                // eslint-disable-next-line camelcase
                item_category4,
            ]
                .filter(Boolean)
                .join('/');

            return normalized;
        };

        const product = {
            item_name: 'Donut Friday Scented T-Shirt',
            item_id: '67890',
            price: '33.75',
            item_brand: 'Google',
            item_category: 'Apparel',
            item_category2: 'Mens',
            item_category3: 'Shirts',
            item_category4: 'Tshirts',
            item_variant: 'Black',
            promotion_id: 'abc123',
            promotion_name: 'summer_promo',
            creative_name: 'instore_suummer',
            creative_slot: '1',
            location_id: 'hero_banner',
            index: 1,
            quantity: '1',
        };
        emitterCb({
            event: 'view_item',
            ecommerce: {
                items: [product],
            },
        });

        let [params] = paramsStub.getCall(0).args;

        chai.expect(params).to.deep.equal({
            __ym: {
                ecommerce: [
                    {
                        detail: {
                            [ECOMMERCE_PRODUCTS]: [
                                normalizeGoogleProduct(product),
                            ],
                        },
                    },
                ],
            },
        });
        const purchaseProduct1 = {
            item_name: 'Triblend Android T-Shirt',
            item_id: '12345',
            item_price: '15.25',
            item_brand: 'Google',
            item_category: 'Apparel',
            item_variant: 'Gray',
            quantity: 1,
            item_coupon: '123',
        };
        const purchaseProduct2 = {
            item_name: 'Donut Friday Scented T-Shirt',
            item_id: '67890',
            item_price: '33.75',
            item_brand: 'Google',
            item_category: 'Apparel',
            item_variant: 'Black',
            quantity: 1,
        };
        const purchase = {
            transaction_id: 'T12345',
            affiliation: 'Online Store',
            value: '35.43',
            tax: '4.90',
            shipping: '5.99',
            currency: 'EUR',
            coupon: 'SUMMER_SALE',
            items: [purchaseProduct1, purchaseProduct2],
        };

        const purchaseParams = {
            __ym: {
                ecommerce: [
                    {
                        purchase: {
                            [ECOMMERCE_PRODUCTS]: [
                                normalizeGoogleProduct(purchaseProduct1),
                                normalizeGoogleProduct(purchaseProduct2),
                            ],
                            [ECOMMERCE_ACTION_FIELD]: {
                                id: 'T12345',
                                affiliation: 'Online Store',
                                revenue: '35.43',
                                tax: '4.90',
                                shipping: '5.99',
                                coupon: 'SUMMER_SALE',
                            },
                        },
                        [ECOMMERCE_CURRENCY]: 'EUR',
                    },
                ],
            },
        };

        emitterCb({
            event: 'purchase',
            ecommerce: purchase,
        });
        [params] = paramsStub.getCall(1).args;
        chai.expect(params).to.deep.equal(purchaseParams);

        emitterCb({
            event: 'purchase',
            ecommerce: {
                purchase,
            },
        });
        [params] = paramsStub.getCall(2).args;
        chai.expect(params).to.deep.equal(purchaseParams);
    });
});
