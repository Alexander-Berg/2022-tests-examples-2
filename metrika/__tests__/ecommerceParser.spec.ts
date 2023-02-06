import * as sinon from 'sinon';
import chai from 'chai';
import { CounterOptions } from '@src/utils/counterOptions';
import * as counter from '@src/utils/counter';
import { METHOD_NAME_PARAMS } from '@src/providers/params/const';
import {
    ECOMMERCE_PARSER_GOODS_PARAM,
    ECOMMERCE_PARSER_TOTALS_PARAM,
    sendParams,
} from '@src/providers/ecommerceParser/sender';
import * as waitForBody from '@src/utils/dom/waitForBody';
import * as counterSettings from '@src/utils/counterSettings';
import * as functionUtils from '@src/utils/function';
import { CounterObject } from '@src/utils/counter/type';
import * as task from '@src/utils/async';
import { JSDOMWrapper } from '@src/__tests__/utils/jsdom';
import * as isNativeFn from '@src/utils/function/isNativeFunction/isNativeFn';
import * as domLib from '@src/utils/dom';
import { ecommerceParser } from '../index';
import * as decoder from '../decoder';
import * as encoder from '../encoder';
import * as utils from '../utils';
import * as checkout from '../checkoutParser';
import * as cart from '../cartParser';
import { currencyParser } from '../currencyParser';
import { priceParser } from '../priceParser';
import { MAX_TITLE_LENGTH } from '../cartParser';

type sendParamsArgument = {
    __ym: {
        [ECOMMERCE_PARSER_TOTALS_PARAM]: string;
        [ECOMMERCE_PARSER_GOODS_PARAM]: string;
    };
};

describe('ecommerceParser', () => {
    const url = 'https://yandex.ru';
    const { window: emptyWindow } = new JSDOMWrapper(undefined, { url });
    const sandbox = sinon.createSandbox();
    const counterOptions = {} as CounterOptions;
    const currency = 'RUB';
    const stubCurrencyId = '643';
    const encoderValue = 'encoderValue';
    const total = 12345.67;
    const quantity = 1;
    const quantity2 = 2;
    const title = 'title';
    const randomNumber = '22';
    const goodsRawData = [[total], [quantity], [title]];
    const goodsRawData2 = [[total], [quantity2], [title]];
    const goodsEncodedData = 'AgAAFHTp3O9u9uVdOVdSz0S7GNvx8cuf';

    let decoderStub: sinon.SinonStub<
        Parameters<typeof decoder.decoder>,
        ReturnType<typeof decoder.decoder>
    >;
    let totalsEncoderStub: sinon.SinonStub<
        Parameters<typeof encoder.totalsEncoder>,
        ReturnType<typeof encoder.totalsEncoder>
    >;
    let huffmanEncoderStub: sinon.SinonStub<
        Parameters<typeof encoder.huffmanEncoder>,
        ReturnType<typeof encoder.huffmanEncoder>
    >;
    let paramsSpy: sinon.SinonSpy<[sendParamsArgument], void>;
    let cartParserSpy: sinon.SinonSpy<
        Parameters<typeof cart.cartParser>,
        ReturnType<typeof cart.cartParser>
    >;
    let checkoutParserSpy: sinon.SinonSpy<
        Parameters<typeof checkout.checkoutParser>,
        ReturnType<typeof checkout.checkoutParser>
    >;

    const cartPathName = '/cart/';
    const cartSearch = '?id=123';

    const checkoutPathName = '/checkout/';
    const checkoutHash = '#/hash';

    const cartUrlTemplate = cartPathName;
    const cartCurrencySelector = '#currency';
    const cartTotalPricesSelector = '#total';

    const cartMobileUrlTemplate = '/mobile-cart/';
    const cartMobileCurrencySelector = '#mobile-currency';
    const cartMobileTotalPricesSelector = '#mobile-total';

    const checkoutUrlTemplate = `${checkoutPathName}${checkoutHash}`;
    const checkoutPlaceOrderBtn = '#checkout-btn';

    const checkoutMobileUrlTemplate = '/mobile-checkout';
    const checkoutMobilePlaceOrderBtn = '#mobile-checkout-btn';

    const cartPricesSelector = '.price';
    const cartQuantitiesSelector = '.qty';
    const cartTitlesSelector = '.title';

    const cartMobilePricesSelector = cartPricesSelector;
    const cartMobileQuantitiesSelector = cartQuantitiesSelector;
    const cartMobileTitlesSelector = cartTitlesSelector;

    const totalWithCurrencySelector = '#same';

    const sendParamsCartValueWithGoods: sendParamsArgument = {
        __ym: {
            [ECOMMERCE_PARSER_TOTALS_PARAM]: encoderValue,
            [ECOMMERCE_PARSER_GOODS_PARAM]: goodsEncodedData,
        },
    };
    const sendParamsCartValueWithoutGoods: sendParamsArgument = {
        __ym: {
            [ECOMMERCE_PARSER_TOTALS_PARAM]: encoderValue,
            [ECOMMERCE_PARSER_GOODS_PARAM]: randomNumber.toString(),
        },
    };
    const sendParamsCheckoutValue: sendParamsArgument = {
        __ym: {
            [ECOMMERCE_PARSER_TOTALS_PARAM]: randomNumber.toString(),
            [ECOMMERCE_PARSER_GOODS_PARAM]: randomNumber.toString(),
        },
    };

    const allSelectors = [
        cartUrlTemplate,
        cartCurrencySelector,
        cartTotalPricesSelector,
        cartMobileUrlTemplate,
        cartMobileCurrencySelector,
        cartMobileTotalPricesSelector,
        checkoutUrlTemplate,
        checkoutPlaceOrderBtn,
        checkoutMobileUrlTemplate,
        checkoutMobilePlaceOrderBtn,
        cartPricesSelector,
        cartQuantitiesSelector,
        cartTitlesSelector,
        cartMobilePricesSelector,
        cartMobileQuantitiesSelector,
        cartMobileTitlesSelector,
    ];

    function stubQuerySelectors() {
        sandbox
            .stub(cart, 'getManyTexts')
            .callsFake((ctx: Window, selector?: string) => {
                switch (selector) {
                    case cartPricesSelector:
                        return [`${total}`];
                    case cartTitlesSelector:
                        return [title];
                    case cartMobilePricesSelector:
                        return [`${total}`];
                    case cartMobileTitlesSelector:
                        return [title];
                    default:
                        return [];
                }
            });
        // NOTE: getManyTexts stub fails in pipe, thus stub at parent function level
        sandbox
            .stub(cart, 'getQuantities')
            .onFirstCall()
            .returns([quantity])
            .onSecondCall()
            .returns([quantity2]);
    }

    beforeEach(() => {
        sandbox.stub(task, 'taskFork').callsFake((reject, resolve) => resolve);
        sandbox.stub(waitForBody, 'waitForBodyTask').callsFake((() =>
            (callback: Function) => {
                callback();
            }) as any);
        sandbox
            .stub(cart, 'getOneText')
            .callsFake((ctx: Window, selector?: string) => {
                switch (selector) {
                    case cartCurrencySelector:
                        return currency;
                    case cartTotalPricesSelector:
                        return `${total}`;
                    case cartMobileCurrencySelector:
                        return currency;
                    case cartMobileTotalPricesSelector:
                        return `${total}`;
                    case totalWithCurrencySelector:
                        return `${total} ${currency}`;
                    default:
                        return '';
                }
            });

        paramsSpy = sandbox.spy((params) => {});
        sandbox.stub(domLib, 'isQuerySelectorSupported').returns(true);
        paramsSpy = sandbox.spy((params) => {});
        cartParserSpy = sandbox.spy(cart, 'cartParser');
        checkoutParserSpy = sandbox.spy(checkout, 'checkoutParser');

        sandbox.stub(counter, 'getCounterInstance').returns({
            [METHOD_NAME_PARAMS]: paramsSpy,
        } as unknown as CounterObject);
        sandbox.stub(functionUtils, 'isNativeFunction').returns(true);

        decoderStub = sandbox.stub(decoder, 'decoder');
        totalsEncoderStub = sandbox
            .stub(encoder, 'totalsEncoder')
            .returns(encoderValue);
        huffmanEncoderStub = sandbox
            .stub(encoder, 'huffmanEncoder')
            .returns(goodsEncodedData);
        sandbox
            .stub(utils, 'generateRandomTwoDigitNumber')
            .returns(randomNumber);

        sandbox
            .stub(counterSettings, 'getCounterSettings')
            .callsFake((_, _1, fn) =>
                Promise.resolve(
                    fn({ settings: { auto_goals: 1, dr: '' } } as any),
                ),
            );

        sandbox.stub(isNativeFn, 'isNativeFn').returns(true);
    });
    afterEach(() => {
        sandbox.restore();
    });

    it('no send params without match page template', async () => {
        const window = emptyWindow;
        decoderStub.returns(allSelectors);

        await ecommerceParser(window, counterOptions);

        sinon.assert.calledOnce(checkoutParserSpy);
        sinon.assert.calledWith(
            checkoutParserSpy,
            window,
            counterOptions,
            false,
            checkoutPlaceOrderBtn,
            checkoutMobilePlaceOrderBtn,
        );
        sinon.assert.notCalled(cartParserSpy);
        sinon.assert.notCalled(totalsEncoderStub);
        sinon.assert.notCalled(huffmanEncoderStub);
        sinon.assert.notCalled(paramsSpy);
    });

    it('no send params without selectors', async () => {
        const { window } = new JSDOMWrapper(undefined, {
            url: `${url}${cartPathName}${cartSearch}`,
        });
        decoderStub.returns([]);

        await ecommerceParser(window, counterOptions);

        sinon.assert.calledOnce(checkoutParserSpy);
        sinon.assert.calledWith(
            checkoutParserSpy,
            window,
            counterOptions,
            false,
        );
        sinon.assert.notCalled(cartParserSpy);
        sinon.assert.notCalled(totalsEncoderStub);
        sinon.assert.notCalled(huffmanEncoderStub);
        sinon.assert.notCalled(paramsSpy);
    });

    it('send total price and currency in params with match cart page template', async () => {
        const { window } = new JSDOMWrapper(undefined, {
            url: `${url}${cartPathName}${cartSearch}`,
        });

        decoderStub.returns(allSelectors);
        sandbox.stub(cart, 'getManyTexts').callsFake(() => []);

        await ecommerceParser(window, counterOptions);

        sinon.assert.calledOnce(cartParserSpy);
        sinon.assert.calledWith(
            cartParserSpy,
            window,
            counterOptions,
            cartCurrencySelector,
            cartTotalPricesSelector,
            cartPricesSelector,
            cartQuantitiesSelector,
            cartTitlesSelector,
        );
        sinon.assert.calledOnceWithExactly(
            checkoutParserSpy,
            window,
            counterOptions,
            false,
            checkoutPlaceOrderBtn,
            checkoutMobilePlaceOrderBtn,
        );
        sinon.assert.calledOnceWithExactly(
            totalsEncoderStub,
            window,
            total,
            stubCurrencyId,
        );
        sinon.assert.notCalled(huffmanEncoderStub);
        sinon.assert.calledOnceWithExactly(
            paramsSpy,
            sendParamsCartValueWithoutGoods,
        );
    });

    it('send all data in params with match cart page template', async () => {
        const { window } = new JSDOMWrapper(undefined, {
            url: `${url}${cartPathName}${cartSearch}`,
        });

        decoderStub.returns(allSelectors);
        stubQuerySelectors();

        await ecommerceParser(window, counterOptions);

        sinon.assert.calledOnce(cartParserSpy);
        sinon.assert.calledWith(
            cartParserSpy,
            window,
            counterOptions,
            cartCurrencySelector,
            cartTotalPricesSelector,
            cartPricesSelector,
            cartQuantitiesSelector,
            cartTitlesSelector,
        );
        sinon.assert.calledOnceWithExactly(
            checkoutParserSpy,
            window,
            counterOptions,
            false,
            checkoutPlaceOrderBtn,
            checkoutMobilePlaceOrderBtn,
        );
        sinon.assert.calledOnceWithExactly(
            totalsEncoderStub,
            window,
            total,
            stubCurrencyId,
        );
        sinon.assert.calledOnceWithExactly(
            huffmanEncoderStub,
            window,
            goodsRawData,
        );
        sinon.assert.calledOnceWithExactly(
            paramsSpy,
            sendParamsCartValueWithGoods,
        );
    });

    it('send total price and currency in params with match mobile cart page template', async () => {
        const { window } = new JSDOMWrapper(undefined, {
            url: `${url}${cartMobileUrlTemplate}`,
        });
        decoderStub.returns(allSelectors);

        await ecommerceParser(window, counterOptions);

        sinon.assert.calledOnce(cartParserSpy);
        sinon.assert.calledWith(
            cartParserSpy,
            window,
            counterOptions,
            cartMobileCurrencySelector,
            cartMobileTotalPricesSelector,
            cartPricesSelector,
            cartQuantitiesSelector,
            cartTitlesSelector,
        );
        sinon.assert.calledOnceWithExactly(
            checkoutParserSpy,
            window,
            counterOptions,
            false,
            checkoutPlaceOrderBtn,
            checkoutMobilePlaceOrderBtn,
        );
        sinon.assert.calledOnceWithExactly(
            totalsEncoderStub,
            window,
            total,
            stubCurrencyId,
        );
        sinon.assert.notCalled(huffmanEncoderStub);
        sinon.assert.calledOnceWithExactly(
            paramsSpy,
            sendParamsCartValueWithoutGoods,
        );
    });

    it('send params with match checkout page template', async () => {
        const { window } = new JSDOMWrapper(undefined, {
            url: `${url}${checkoutPathName}${checkoutHash}`,
        });
        decoderStub.returns(allSelectors);

        await ecommerceParser(window, counterOptions);

        sinon.assert.notCalled(cartParserSpy);
        sinon.assert.calledOnceWithExactly(
            checkoutParserSpy,
            window,
            counterOptions,
            true,
            checkoutPlaceOrderBtn,
            checkoutMobilePlaceOrderBtn,
        );
        sinon.assert.notCalled(totalsEncoderStub);
        sinon.assert.notCalled(huffmanEncoderStub);
        sinon.assert.calledOnceWithExactly(paramsSpy, sendParamsCheckoutValue);
    });

    it('send params with match mobile checkout page template', async () => {
        const { window } = new JSDOMWrapper(undefined, {
            url: `${url}${checkoutMobileUrlTemplate}`,
        });
        decoderStub.returns(allSelectors);

        await ecommerceParser(window, counterOptions);

        sinon.assert.notCalled(cartParserSpy);
        sinon.assert.calledOnceWithExactly(
            checkoutParserSpy,
            window,
            counterOptions,
            true,
            checkoutPlaceOrderBtn,
            checkoutMobilePlaceOrderBtn,
        );
        sinon.assert.notCalled(totalsEncoderStub);
        sinon.assert.calledOnceWithExactly(paramsSpy, sendParamsCheckoutValue);
    });

    describe('cartParser', () => {
        it('send params on call with empty selectors', () => {
            const window = emptyWindow;
            cart.cartParser(window, counterOptions, '', '', '', '', '');

            sinon.assert.calledOnceWithExactly(
                totalsEncoderStub,
                window,
                0,
                '643',
            );
            sinon.assert.notCalled(huffmanEncoderStub);
            sinon.assert.calledOnceWithExactly(
                paramsSpy,
                sendParamsCartValueWithoutGoods,
            );
        });

        it('send params on call with existing selectors', () => {
            const window = emptyWindow;
            stubQuerySelectors();

            cart.cartParser(
                window,
                counterOptions,
                cartCurrencySelector,
                cartTotalPricesSelector,
                cartPricesSelector,
                cartQuantitiesSelector,
                cartTitlesSelector,
            );

            sinon.assert.calledOnceWithExactly(
                totalsEncoderStub,
                window,
                total,
                stubCurrencyId,
            );
            sinon.assert.calledOnceWithExactly(
                huffmanEncoderStub,
                window,
                goodsRawData,
            );
            sinon.assert.calledOnceWithExactly(
                paramsSpy,
                sendParamsCartValueWithGoods,
            );
        });

        it('send params on change selector value', async () => {
            const { window } = new JSDOMWrapper(`<div id="change-it"></div>`, {
                url,
            });
            stubQuerySelectors();

            cart.cartParser(
                window,
                counterOptions,
                totalWithCurrencySelector,
                totalWithCurrencySelector,
                cartPricesSelector,
                cartQuantitiesSelector,
                cartTitlesSelector,
            );

            const existingDivElement =
                window.document.querySelector('#change-it');
            const newSpanElement = window.document.createElement('span');
            await existingDivElement!.appendChild(newSpanElement);

            sinon.assert.calledTwice(totalsEncoderStub);
            sinon.assert.calledWithExactly(
                totalsEncoderStub.getCall(0),
                window,
                total,
                stubCurrencyId,
            );
            sinon.assert.calledWithExactly(
                totalsEncoderStub.getCall(1),
                window,
                total,
                stubCurrencyId,
            );

            sinon.assert.calledTwice(huffmanEncoderStub);
            sinon.assert.calledWithExactly(
                huffmanEncoderStub.getCall(0),
                window,
                goodsRawData,
            );
            sinon.assert.calledWithExactly(
                huffmanEncoderStub.getCall(1),
                window,
                goodsRawData2,
            );

            sinon.assert.calledTwice(paramsSpy);
            sinon.assert.calledWithExactly(
                paramsSpy.getCall(0),
                sendParamsCartValueWithGoods,
            );
            sinon.assert.calledWithExactly(
                paramsSpy.getCall(1),
                sendParamsCartValueWithGoods,
            );
        });

        it('limits title length', () => {
            const window = emptyWindow;
            const longTitle = title.repeat(
                Math.ceil(MAX_TITLE_LENGTH / title.length) + 1,
            );
            chai.assert(longTitle.length > MAX_TITLE_LENGTH);

            sandbox
                .stub(cart, 'getManyTexts')
                .callsFake((ctx: Window, selector?: string) => {
                    switch (selector) {
                        case cartTitlesSelector:
                            return [longTitle];
                        default:
                            return [`${total}`];
                    }
                });
            // NOTE: getManyTexts stub fails in pipe, thus stub at parent function level
            sandbox.stub(cart, 'getQuantities').returns([quantity]);

            cart.cartParser(
                window,
                counterOptions,
                cartCurrencySelector,
                cartTotalPricesSelector,
                cartPricesSelector,
                cartQuantitiesSelector,
                cartTitlesSelector,
            );

            sinon.assert.calledOnceWithExactly(huffmanEncoderStub, window, [
                [total],
                [quantity],
                [longTitle.slice(0, MAX_TITLE_LENGTH)],
            ]);
        });
    });

    describe('checkoutParser', () => {
        const window = {} as Window;
        it('send params on checkout page', () => {
            checkout.checkoutParser(window, counterOptions, true, '', '');
            sinon.assert.calledOnceWithExactly(
                paramsSpy,
                sendParamsCheckoutValue,
            );
        });

        it('no send', () => {
            checkout.checkoutParser(window, counterOptions, false, '', '');
            sinon.assert.notCalled(paramsSpy);
        });
    });

    describe('currencyParser', () => {
        it('return 643 without math', () => {
            ['', '123', 'abc', ' ', '.'].forEach((testValue) => {
                chai.expect(currencyParser(testValue)).to.be.equal('643');
            });
        });

        describe('return valid currencyId', () => {
            [
                {
                    currencyId: '978',
                    tests: ['9320 EUR', '1€'],
                },
                {
                    currencyId: '840',
                    tests: ['1 USD', '1$', '1У.Е.'],
                },
                {
                    currencyId: '980',
                    tests: ['1 UAH', 'ГРН', '₴'],
                },
                {
                    currencyId: '643',
                    tests: [
                        '2 RUR',
                        '1RUB',
                        '10Р',
                        'РУБ',
                        '₽',
                        'P',
                        ' РUB',
                        'PУБ',
                        'PУB',
                        'PYБ',
                        'РYБ',
                        'РУB',
                        'PУБ',
                    ],
                },
                {
                    currencyId: '398',
                    tests: ['ТГ', 'KZT', '₸', 'ТҢГ.', 'TENGE', 'ТЕНГЕ'],
                },
                {
                    currencyId: '826',
                    tests: ['GBP', '£', 'UKL'],
                },
            ].forEach(({ currencyId, tests }) => {
                tests.forEach((test) => {
                    it(`match ${currencyId} on ${test}`, () => {
                        chai.expect(currencyParser(test)).to.be.equal(
                            currencyId,
                        );
                    });
                });
            });
        });
    });

    describe('priceParser', () => {
        // eslint-disable-next-line no-restricted-globals
        const window = { isNaN, Math } as Window;
        it('return 0 without math', () => {
            ['', 'asd', 'e', ' ', '.'].forEach((testValue) => {
                chai.expect(priceParser(window, testValue)).to.be.equal(0);
            });
        });

        describe('return valid price', () => {
            [
                {
                    price: 978,
                    tests: ['978', '978.0', '978 ₽', '(978)'],
                },
                {
                    price: 12333.33,
                    tests: [
                        '12333.33',
                        '12333,33',
                        '12 333.33',
                        '12 333,33',
                        '12.333,33',
                    ],
                },
            ].forEach(({ price, tests }) => {
                tests.forEach((test) => {
                    it(`match ${price} on ${test}`, () => {
                        chai.expect(priceParser(window, test)).to.be.equal(
                            price,
                        );
                    });
                });
            });
        });
    });

    describe('sendParams', () => {
        const window = { Math } as Window;
        it('send params without data', () => {
            sendParams(window, {} as CounterOptions);
            sinon.assert.calledOnceWithExactly(
                paramsSpy,
                sendParamsCheckoutValue,
            );
        });

        it('send params with total price and currency', () => {
            sendParams(window, {} as CounterOptions, encoderValue, '');
            sinon.assert.calledOnceWithExactly(
                paramsSpy,
                sendParamsCartValueWithoutGoods,
            );
        });

        it('send params with all data', () => {
            sendParams(
                window,
                {} as CounterOptions,
                encoderValue,
                goodsEncodedData,
            );
            sinon.assert.calledOnceWithExactly(
                paramsSpy,
                sendParamsCartValueWithGoods,
            );
        });

        it('send params with titles length restricted', () => {
            sendParams(
                window,
                {} as CounterOptions,
                encoderValue,
                goodsEncodedData,
            );
            sinon.assert.calledOnceWithExactly(
                paramsSpy,
                sendParamsCartValueWithGoods,
            );
        });
    });
});
