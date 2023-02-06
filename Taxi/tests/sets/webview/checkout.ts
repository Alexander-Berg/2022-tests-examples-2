import {expect} from 'chai'

import {CardPaymentMethod} from '@lavka/api-typings/schemas/api-proxy-superapp-critical/paymentmethods'
import {identifiers} from '@lavka/constants'
import {
  waitAndAssertClientRequest,
  makeFutureBackendResponsesCookie,
  modifyFutureBackendResponses,
  makeExperimentsCookies,
} from '@lavka/tests'

import {DEFAULT_CART_CASHBACK_WALLET, HEADER_SCROLL_COMPENSATION, HUGE_COMMENT_1, HUGE_COMMENT_2} from '../../constants'
import {CheckoutPage, MainPage, TrackingPage, VerificationCardPage} from '../../models'
import {makeMockServerResponseData} from '../../utils'

describe('Чекаут', async function () {
  const epsilonOptions = {
    cookies: {
      cartRetrieveId: identifiers.cartRetrieveEpsilon,
      cartPromocodesListId: identifiers.cartPromocodesListEpsilon,
      useCartService: 'true',
    },
  }

  const submitDefaultPosition = {
    entrance: '6',
    flat: '231',
    location: [37.642474, 55.735525],
    place_id:
      'ymapsbm1://geo?ll=37.642%2C55.736&spn=0.001%2C0.001&text=%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D1%8F%2C%20%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0%2C%20%D0%A1%D0%B0%D0%B4%D0%BE%D0%B2%D0%BD%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B0%D1%8F%20%D1%83%D0%BB%D0%B8%D1%86%D0%B0%2C%2082%D1%812',
    postal_code: '115035',
  }

  const marksistkayaPosition = {
    location: [37.65560702918062, 55.740785708144216],
    place_id:
      'ymapsbm1://geo?ll=37.656%2C55.741&spn=0.001%2C0.001&text=%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D1%8F%2C%20%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0%2C%20%D0%9C%D0%B0%D1%80%D0%BA%D1%81%D0%B8%D1%81%D1%82%D1%81%D0%BA%D0%B0%D1%8F%20%D1%83%D0%BB%D0%B8%D1%86%D0%B0%2C%202',
    postal_code: '109147',
  }

  it('Страница чекаута загружается', async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage(epsilonOptions)
    await checkout.assertImage({state: 'loaded'}, {waitForCartButtonActive: true})
  })

  it('Скролл к разным блокам чекаута', async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage(epsilonOptions)
    await checkout.scrollToLayoutPageBlock('address', {offsetY: HEADER_SCROLL_COMPENSATION})
    await checkout.assertImage({state: 'scrolled-to-address'}, {waitForCartButtonActive: true})
    await checkout.scrollToLayoutPageBlock('instructions', {offsetY: HEADER_SCROLL_COMPENSATION})
    await checkout.assertImage({state: 'scrolled-to-instructions'})
    await checkout.scrollToLayoutPageBlock('plus', {offsetY: HEADER_SCROLL_COMPENSATION})
    await checkout.assertImage({state: 'scrolled-to-plus'})
    await checkout.scrollToLayoutPageBlock('payment')
    await checkout.assertImage({state: 'scrolled-to-payment'})
  })

  it('Чекаут открывается и дёргаются ручки: list-payment-methods => set-cashback-flow => set-payment-method', async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage(epsilonOptions)
    await waitAndAssertClientRequest(this, 'payments/v1/list-payment-methods', {haveBeenCalledTimes: 1})
    await waitAndAssertClientRequest(this, 'cart/v1/set-payment', {
      haveBeenCalledTimes: 1,
      calledAfter: ['payments/v1/list-payment-methods', {haveBeenCalledTimes: 1}],
    })
    await waitAndAssertClientRequest(this, 'cart/v1/set-cashback-flow', {
      haveBeenCalledTimes: 1,
      calledAfter: ['cart/v1/set-payment', {haveBeenCalledTimes: 1}],
    })
  })

  it('После оплаты заказа идёт переход на страницу трекинга, можно вернуться на главную и увидеть заказ', async function () {
    const checkout = new CheckoutPage(this)
    const tracking = new TrackingPage(this)
    const mainPage = new MainPage(this)
    await checkout.openPage(epsilonOptions)
    await checkout.clickAvailablePayButton()
    await tracking.waitForLayout()
    const url = new URL(await this.browser.getUrl())
    expect(url.pathname).to.be.includes('lavka/order/sadovnicheskaya82c2OrderId')
    /* страница трекинга не отражает текущую корзину, это не важно для теста */
    await tracking.assertImage({state: 'tracking-page-opened'})
    await tracking.clickToolbarBackButton()
    await mainPage.waitForPageLoaded()
    await mainPage.assertImage({state: 'returned-to-main-page'})
  })

  it('yalavka-223,229: Баллы плюса. Выбор списания без полной оплаты кешбеком, затем оплата', async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage(epsilonOptions)
    await checkout.waitForLayoutPageBlockExists('plus')
    await checkout.scrollToLayoutPageBlock('plus', {offsetY: HEADER_SCROLL_COMPENSATION})
    await modifyFutureBackendResponses(this, {
      'cart:cashback:full_payment': false,
    })
    await checkout.clickCashbackRadioToggle('charge')
    await waitAndAssertClientRequest(this, 'cart/v1/set-cashback-flow', {haveBeenCalledTimes: 2})
    await checkout.assertImage({state: 'before-order-pay'}, {waitForCartButtonActive: true})
    await checkout.clickAvailablePayButton()
    await waitAndAssertClientRequest(this, 'orders/v2/submit', {
      haveBeenCalledTimes: 1,
      matchDeepInclude: {
        cashback: {cashback_to_pay: '54', wallet_id: DEFAULT_CART_CASHBACK_WALLET},
      },
    })
  })
  it('yalavka-224,229: Баллы плюса. Выбор списания с полной оплатой кешбеком и затем выбор не списывать, затем оплата', async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage(epsilonOptions)
    await checkout.waitForLayoutPageBlockExists('plus')
    await checkout.scrollToLayoutPageBlock('plus', {offsetY: HEADER_SCROLL_COMPENSATION})
    await modifyFutureBackendResponses(this, {
      'cart:cashback:full_payment': true,
    })
    await checkout.clickCashbackRadioToggle('charge')
    await waitAndAssertClientRequest(this, 'cart/v1/set-cashback-flow', {haveBeenCalledTimes: 2})
    await checkout.assertImage({state: 'selected-charge-cashback'}, {waitForCartButtonActive: true})
    await checkout.clickCashbackRadioToggle('gain')
    await waitAndAssertClientRequest(this, 'cart/v1/set-cashback-flow', {haveBeenCalledTimes: 3})
    await checkout.assertImage({state: 'selected-do-not-charge-cashback'}, {waitForCartButtonActive: true})
    await checkout.clickAvailablePayButton()
    await waitAndAssertClientRequest(this, 'orders/v2/submit', {
      haveBeenCalledTimes: 1,
      matchDeepInclude: {
        cashback: {wallet_id: DEFAULT_CART_CASHBACK_WALLET, cashback_to_pay: null},
      },
    })
  })
  it('yalavka-225: Промокоды. Активация промокодов по очереди', async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage(epsilonOptions)
    await checkout.scrollToLayoutPageBlock('payment')
    await checkout.waitAndClickPromocodeCoupon(identifiers.promocodeEpsilon1)
    await waitAndAssertClientRequest(this, 'cart/v1/apply-promocode', {haveBeenCalledTimes: 1})
    await checkout.assertImage({state: 'first-promocode-clicked'}, {waitForCartButtonActive: true})
    await checkout.waitAndClickPromocodeCoupon(identifiers.promocodeEpsilon3)
    await waitAndAssertClientRequest(this, 'cart/v1/apply-promocode', {haveBeenCalledTimes: 2})
    await checkout.assertCouponValue(identifiers.promocodeEpsilon3, 'true')
    await checkout.assertCouponValue(identifiers.promocodeEpsilon1, 'false')
  })
  it('yalavka-225: Промокоды. Отображение и клик по недоступному промокоду', async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage(epsilonOptions)
    await checkout.waitForCouponExists(identifiers.promocodeEpsilon2)
    await checkout.scrollCouponListToCoupon(identifiers.promocodeEpsilon2)
    await checkout.assertImage({state: 'scrolled-to-promocode-2'}, {waitForCartButtonActive: true})
    await checkout.assertCouponValue(identifiers.promocodeEpsilon2, 'false')
  })
  it('yalavka-226: Промокоды. Деактивация активированного промокода', async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage(epsilonOptions)
    await checkout.waitAndClickPromocodeCoupon(identifiers.promocodeEpsilon1)
    await waitAndAssertClientRequest(this, 'cart/v1/apply-promocode', {haveBeenCalledTimes: 1})
    await checkout.assertCouponValue(identifiers.promocodeEpsilon1, 'true')
    await checkout.waitAndClickPromocodeCoupon(identifiers.promocodeEpsilon1)
    await waitAndAssertClientRequest(this, 'cart/v1/apply-promocode', {haveBeenCalledTimes: 2})
    await checkout.assertImage({state: 'coupon-1-switched-to-disabled'}, {waitForCartButtonActive: true})
    await checkout.assertCouponValue(identifiers.promocodeEpsilon1, 'false')
  })
  it('yalavka-227: Отображается первый способ оплаты из списка, если последний выбранный способ оплаты не пришёл', async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage(epsilonOptions)
    await checkout.waitForSelectedPaymentMethod('card')
    await checkout.scrollToLayoutPageBlock('payment')
    await checkout.assertImage({state: 'loaded-payment-method'}, {waitForCartButtonActive: true})
  })
  it('yalavka-227: Отображается последний выбранный способ оплаты (карта МИР)', async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage({
      cookies: {
        ...epsilonOptions.cookies,
        ...makeFutureBackendResponsesCookie({
          'list-payment-methods:last_used_payment_method': {
            type: 'card',
            id: 'card-x8af859f142289e3279eb0e4d',
          } as CardPaymentMethod,
        }),
      },
    })
    await checkout.waitForSelectedPaymentMethod('card')
    await checkout.scrollToLayoutPageBlock('payment')
    await checkout.assertImage({state: 'loaded-card-payment-method'}, {waitForCartButtonActive: true})
  })
  it('yalavka-227: Отображается последний выбранный способ оплаты (карта mastercard), который требует верификацию', async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage({
      cookies: {
        ...epsilonOptions.cookies,
        ...makeFutureBackendResponsesCookie({
          'list-payment-methods:last_used_payment_method': {
            type: 'card',
            id: 'card-x900a72792f23eb2b0b46966a',
          } as CardPaymentMethod,
        }),
        ...makeExperimentsCookies({'lavka-frontend_web-payment-method': {paymentsWithCartBindingEnabled: true}}),
      },
    })
    await checkout.waitForSelectedPaymentMethod('card')
    await checkout.scrollToLayoutPageBlock('payment')
    await checkout.assertImage({state: 'loaded-payment-method'})
  })
  it('yalavka-227: Не даем выбрать apple pay, если включен эксп lavka-frontend_payment-methods-disabling, боттом шит не закроется', async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage({
      cookies: {
        ...epsilonOptions.cookies,
        ...makeMockServerResponseData({
          responseNativePaymentMethods: [{type: 'applepay'}],
          responseNativeLastUsedPaymentMethod: null,
        }),
        ...makeExperimentsCookies({
          'lavka-frontend_payment-methods-disabling': {paymentMethods: ['applepay', 'googlepay']},
        }),
      },
    })
    await checkout.waitAndClickForSelectedPaymentMethod({waitForCartButtonActive: true})
    await checkout.assertImage({state: 'payment-methods-opened'})
    await checkout.selectPaymentMethodInBottomSheet({type: 'applepay'}, {skipWaitingForCloseBottomSheet: true})
    await this.browser.pause(100)
    await checkout.assertImage({state: 'payment-method-has-not-changed'})
  })
  // TODO: заменить на последний вебный способ оплаты, от сигналов натива отказываемся
  // it('yalavka-227: Отображается последний выбранный нативный способ оплаты (applepay)', async function () {
  //   const checkout = new CheckoutPage(this)
  //   await checkout.openPage({
  //     cookies: {
  //       ...epsilonOptions.cookies,
  //       ...makeMockServerResponseData({
  //         responseNativePaymentMethods: [{type: 'applepay'}],
  //         responseNativeLastUsedPaymentMethod: {type: 'applepay'},
  //       }),
  //     },
  //   })
  //   await checkout.scrollToLayoutPageBlock('payment')
  //   await checkout.waitForSelectedPaymentMethod('applepay')
  //   await checkout.assertImage({state: 'loaded-payment-method'}, {waitForCartButtonActive: true})
  // })
  it('yalavka-227: В боттомшите не отображается ничего, если в list-payment-methods нет способов оплат, а сигнал натива их вернул', async function () {
    /* заодно проверяем отображение пустого боттом шита */
    const checkout = new CheckoutPage(this)
    await checkout.openPage({
      cookies: {
        ...epsilonOptions.cookies,
        ...makeMockServerResponseData({
          responseNativePaymentMethods: [{type: 'applepay'}],
          responseNativeLastUsedPaymentMethod: {type: 'applepay'},
        }),
        ...makeFutureBackendResponsesCookie({'list-payment-methods:payment_methods': []}),
      },
    })
    await waitAndAssertClientRequest(this, 'payments/v1/list-payment-methods', {
      haveBeenCalledTimes: 1,
    })
    await checkout.scrollToLayoutPageBlock('payment')
    await checkout.assertImage({
      state: 'loaded-without-selected-payment-method',
    })
    await checkout.waitAndClickForSelectedPaymentMethod()
    await checkout.assertImage({
      state: 'payment-methods-opened',
    })
  })
  it('yalavka-227: Клик по доступному способу оплаты (карта), изначально выбрана произвольная карта МИР', async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage({
      cookies: {
        ...epsilonOptions.cookies,
        ...makeMockServerResponseData({
          responseNativePaymentMethods: [{type: 'applepay'}],
          responseNativeLastUsedPaymentMethod: null,
        }),
        ...makeFutureBackendResponsesCookie({
          'list-payment-methods:last_used_payment_method': {
            type: 'card',
            id: 'card-x8af859f142289e3279eb0e4d',
          } as CardPaymentMethod,
        }),
      },
    })
    await checkout.waitAndClickForSelectedPaymentMethod({waitForCartButtonActive: true})
    await checkout.assertImage({state: 'payment-methods-opened'})
    await checkout.selectPaymentMethodInBottomSheet({id: 'card-x160afe9223ba3c91f43e7cb5'})
    await checkout.assertImage({state: 'selected-first-payment-method'}, {waitForCartButtonActive: true})
    await checkout.waitAndClickForSelectedPaymentMethod({waitForCartButtonActive: true})
    await checkout.assertImage({state: 'bottom-sheet-opened-again'})
    await checkout.selectPaymentMethodInBottomSheet({type: 'applepay'})
    await checkout.assertImage({state: 'apple-pay-selected'}, {waitForCartButtonActive: true})
  })
  it(`yalavka-227: Клик по способу оплаты, и закрытие модалки выборов способ оплат по кнопке 'Закрыть'`, async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage(epsilonOptions)
    await checkout.waitAndClickForSelectedPaymentMethod({waitForCartButtonActive: true})
    await checkout.closeBottomSheetPaymentMethods()
  })
  it('yalavka-227: Клик по способу оплаты, требующего верификацию. Должны перейти на страницу верификации', async function () {
    const checkout = new CheckoutPage(this)
    const verificationCardPage = new VerificationCardPage(this)
    await checkout.openPage(epsilonOptions)
    await checkout.waitAndClickForSelectedPaymentMethod({waitForCartButtonActive: true})
    await checkout.selectPaymentMethodInBottomSheet({id: 'card-xef54fc5c18e5146cba45eba9'})
    const url = new URL(await this.browser.getUrl())
    expect(url.searchParams.get('strategy')).equals('additional-verification')
    await verificationCardPage.waitForPageLoaded()
  })
  it('yalavka-227: Клик по способу оплаты, требующего допривязку. Должны перейти на страницу верификации', async function () {
    const checkout = new CheckoutPage(this)
    const verificationCardPage = new VerificationCardPage(this)
    await checkout.openPage(epsilonOptions)
    await checkout.waitAndClickForSelectedPaymentMethod({waitForCartButtonActive: true})
    await checkout.selectPaymentMethodInBottomSheet({id: 'card-x900a72792f23eb2b0b46966a'})
    const url = new URL(await this.browser.getUrl())
    expect(url.searchParams.get('strategy')).equals('binding-verification')
    await verificationCardPage.waitForPageLoaded()
  })
  it('yalavka-227: Оплата картой, после выбора из боттом шита', async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage(epsilonOptions)
    await checkout.waitAndClickForSelectedPaymentMethod({waitForCartButtonActive: true})
    await checkout.selectPaymentMethodInBottomSheet({id: 'card-x160afe9223ba3c91f43e7cb5'})
    await checkout.clickAvailablePayButton()
    await waitAndAssertClientRequest(this, 'orders/v2/submit', {
      haveBeenCalledTimes: 1,
      matchDeepInclude: {payment_method_id: 'card-x160afe9223ba3c91f43e7cb5', payment_method_type: 'card'},
    })
  })
  // TODO: заменить на последний вебный способ оплаты, от сигналов натива отказываемся
  // it('yalavka-228: Отображается последний выбранный нативный способ оплаты (corp), который требует верификацию', async function () {
  //   const checkout = new CheckoutPage(this)
  //   await checkout.openPage({
  //     cookies: {
  //       ...epsilonOptions.cookies,
  //       ...makeMockServerResponseData({
  //         responseNativePaymentMethods: [{type: 'corp'}],
  //         responseNativeLastUsedPaymentMethod: {type: 'corp'},
  //       }),
  //     },
  //   })
  //   await checkout.scrollToLayoutPageBlock('payment')
  //   await checkout.waitForSelectedPaymentMethod('corp')
  //   await checkout.assertImage({state: 'loaded-payment-method'})
  // })
  it('yalavka-228: Клик по недоступному способу оплаты (corp). Боттом шит не закроется и способ оплаты не меняется', async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage(epsilonOptions)
    await checkout.waitAndClickForSelectedPaymentMethod({waitForCartButtonActive: true})
    await checkout.selectPaymentMethodInBottomSheet({type: 'corp'}, {skipWaitingForCloseBottomSheet: true})
    await this.browser.pause(100)
    await checkout.assertImage({state: 'payment-method-has-not-changed'})
  })
  it('yalavka-228: Оплата бейджом', async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage({
      cookies: {
        ...epsilonOptions.cookies,
        listPaymentMethodsId: identifiers.listPaymentMethodsWithCorp,
      },
    })
    await checkout.clickAvailablePayButton()
    await waitAndAssertClientRequest(this, 'orders/v2/submit', {
      matchDeepInclude: {
        payment_method_id: 'badge:yandex_badge:RUB',
        payment_method_type: 'corp',
      },
      haveBeenCalledTimes: 1,
    })
  })
  it(`yalavka-230,231,232: Отображение и оплата с флагами 'Не звонить в дверь' и 'Встречу на улице'`, async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage(epsilonOptions)
    await checkout.waitAndClickAddressSwitcher('noDoorCall')
    await checkout.waitAndClickAddressCheckbox('meetOutside')
    await checkout.assertImage({state: 'flags-checked-on'}, {waitForCartButtonActive: true})
    await checkout.clickAvailablePayButton()
    await waitAndAssertClientRequest(this, 'orders/v2/submit', {
      matchDeepInclude: {
        position: {
          ...submitDefaultPosition,
          meet_outside: true,
          no_door_call: true,
        },
      },
      haveBeenCalledTimes: 1,
    })
  })
  it(`yalavka-230,231,232: Отображение и оплата с флагами 'Не звонить в дверь' и 'Оставить у двери'`, async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage(epsilonOptions)
    await checkout.waitAndClickAddressSwitcher('noDoorCall')
    await checkout.waitAndClickAddressCheckbox('meetOutside')
    /* переключаем, чтобы проверить, что meetOutside выключится */
    await checkout.waitAndClickAddressCheckbox('leftAtDoor')
    await checkout.assertImage({state: 'flags-checked-on'}, {waitForCartButtonActive: true})
    await checkout.clickAvailablePayButton()
    await waitAndAssertClientRequest(this, 'orders/v2/submit', {
      matchDeepInclude: {
        position: {
          ...submitDefaultPosition,
          left_at_door: true,
          no_door_call: true,
        },
      },
      haveBeenCalledTimes: 1,
    })
  })
  it(`yalavka-230,231,232: Отображение и оплата с флагами, если имеются только 'Оставить у двери', 'Не звонить в дверь'`, async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage({
      cookies: {
        ...epsilonOptions.cookies,
        checkoutLayoutId: 'checkoutLayoutAlphaId',
      },
    })
    await checkout.scrollToLayoutPageBlock('address', {offsetY: HEADER_SCROLL_COMPENSATION})
    await checkout.assertImage({state: 'flags-checked-off'}, {waitForCartButtonActive: true})
    await checkout.waitAndClickAddressSwitcher('leftAtDoor')
    await checkout.waitAndClickAddressSwitcher('noDoorCall')
    await checkout.assertImage({state: 'flags-checked-on'})
    await checkout.clickAvailablePayButton()
    await waitAndAssertClientRequest(this, 'orders/v2/submit', {
      matchDeepInclude: {
        position: {
          ...submitDefaultPosition,
          left_at_door: true,
          no_door_call: true,
        },
      },
      haveBeenCalledTimes: 1,
    })
  })
  it(`yalavka-234: Ввод комментария и оплата, проверка корректности отправки`, async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage({
      cookies: {
        ...epsilonOptions.cookies,
      },
    })
    await checkout.scrollToLayoutPageBlock('address', {offsetY: HEADER_SCROLL_COMPENSATION})
    await checkout.typeTextToCommentField(HUGE_COMMENT_1, {blurOnEnd: true})
    await checkout.assertImage({state: 'comment-1-entered'}, {waitForCartButtonActive: true})
    await checkout.typeTextToCommentField(HUGE_COMMENT_2, {clearBefore: true})
    await checkout.assertImage({state: 'comment-2-entered'})
    await checkout.clickAvailablePayButton()
    await waitAndAssertClientRequest(this, 'orders/v2/submit', {
      matchDeepInclude: {
        position: {
          ...submitDefaultPosition,
          comment: HUGE_COMMENT_2,
        },
      },
      haveBeenCalledTimes: 1,
    })
  })
  it(`yalavka-240: Удаление cуществующего комментария и оплата, проверка корректности отправки`, async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage({
      cookies: {
        ...epsilonOptions.cookies,
        ...makeFutureBackendResponsesCookie({
          'get-address:comment': HUGE_COMMENT_1,
        }),
      },
    })
    await checkout.scrollToLayoutPageBlock('address', {offsetY: HEADER_SCROLL_COMPENSATION})
    await checkout.assertImage({state: 'loaded-with-comment'}, {waitForCartButtonActive: true})
    await checkout.typeTextToCommentField('', {clearBefore: true})
    await checkout.assertImage({state: 'comment-clean'})
    await checkout.clickAvailablePayButton()
    await waitAndAssertClientRequest(this, 'orders/v2/submit', {
      matchDeepInclude: {
        position: submitDefaultPosition,
      },
      haveBeenCalledTimes: 1,
    })
  })
  it(`yalavka-241: Поле промокода, корректность отображения и применения (если промокода нету в рулетке промокодов)`, async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage(epsilonOptions)
    await checkout.waitAndClickPromocodeField()
    await checkout.scrollToLayoutPageBlock('payment', {offsetY: HEADER_SCROLL_COMPENSATION})
    await checkout.assertImage({state: 'promocode-bottom-sheet-opened'}, {waitForCartButtonActive: true})
    await checkout.typePromocodeText(identifiers.promocodeEpsilonA)
    await checkout.assertImage({state: 'promocode-typed'})
    await checkout.confirmPromocode({waitForBottomSheetClosed: true})
    await waitAndAssertClientRequest(this, 'cart/v1/apply-promocode', {haveBeenCalledTimes: 1})
    await checkout.assertImage({state: 'promocode-confirmed'}, {waitForCartButtonActive: true})
  })
  it(`yalavka-241: Поле промокода, ввод и применение промокодов по очереди из поля, которые также есть в рулетке промокодов`, async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage(epsilonOptions)
    await checkout.scrollToLayoutPageBlock('payment', {offsetY: HEADER_SCROLL_COMPENSATION})
    await checkout.waitAndClickPromocodeField()
    await checkout.typePromocodeText(identifiers.promocodeEpsilon1)
    await checkout.confirmPromocode()
    await waitAndAssertClientRequest(this, 'cart/v1/apply-promocode', {haveBeenCalledTimes: 1})
    await checkout.assertImage({state: 'first-promocode-in-roulette-confirmed'}, {waitForCartButtonActive: true})
    await checkout.waitAndClickPromocodeField()
    await checkout.typePromocodeText(identifiers.promocodeEpsilon3, {clearBefore: true})
    await checkout.confirmPromocode({waitForBottomSheetClosed: true})
    await waitAndAssertClientRequest(this, 'cart/v1/apply-promocode', {haveBeenCalledTimes: 2})
    // await checkout.assertImage({state: 'third-promocode-in-roulette-confirmed'}, {waitForCartButtonActive: true})
  })
  it(`yalavka-241: Применение невалидного промокода, вывод сообщения от валидатора`, async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage(epsilonOptions)
    await checkout.scrollToLayoutPageBlock('payment', {offsetY: HEADER_SCROLL_COMPENSATION})
    await checkout.waitAndClickPromocodeField()
    await checkout.typePromocodeText(identifiers.promocodeEpsilonC)
    await checkout.confirmPromocode()
    await checkout.assertImage({state: 'promocode-failed'}, {waitForCartButtonActive: true})
    await checkout.waitAndClickBottomSheetBackdrop()
    await checkout.assertImage({state: 'promocode-does-not-applied'})
  })
  it(`yalavka-242: Удаление применённого промокода, корректность отображения кнопки при стирании символов промокода`, async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage(epsilonOptions)
    await checkout.scrollToLayoutPageBlock('payment', {offsetY: HEADER_SCROLL_COMPENSATION})
    await checkout.waitAndClickPromocodeField()
    await checkout.typePromocodeText(identifiers.promocodeEpsilon1)
    await checkout.confirmPromocode()
    await checkout.waitAndClickPromocodeField()
    await checkout.typePromocodeText('', {eraseCountSymbols: 3})
    await checkout.assertImage({state: 'removed-some-promocode-symbols'})
    await checkout.clickRemovePromocodeButton({waitForBottomSheetClosed: true})
    await checkout.assertImage({state: 'promocode-removed'})
  })
  it(`yalavka-244: Открытие формы адреса, клик по полям и редактирование полей адреса и оплата`, async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage(epsilonOptions)
    await checkout.scrollToLayoutPageBlock('address', {offsetY: HEADER_SCROLL_COMPENSATION})
    await checkout.waitForCartButtonActive()
    await checkout.waitAndClickAddressField()
    await checkout.waitForDeliveryAddressBottomSheet()
    await checkout.assertImage({state: 'address-bottom-sheet-opened'})
    await checkout.typeAddressBottomSheetAddressFieldText('flat', '556')
    await checkout.typeAddressBottomSheetAddressFieldText('entrance', '8B', {clearBefore: true})
    await checkout.typeAddressBottomSheetAddressFieldText('doorcode', '22key+2')
    await checkout.typeAddressBottomSheetAddressFieldText('floor', '777')
    await checkout.assertImage({state: 'address-fields-entered'})
    await checkout.waitAndClickBottomSheetBackdrop()
    /* убеждаемся, что если открыть снова боттом шит, значения в нём те же */
    await checkout.waitAndClickAddressField()
    await checkout.assertImage({state: 'bottom-sheet-opened-again'})
    await checkout.clickConfirmAddressButton()
    await checkout.assertImage({state: 'bottom-sheet-closed-before-pay'})
    await checkout.clickAvailablePayButton()
    await waitAndAssertClientRequest(this, 'orders/v2/submit', {
      haveBeenCalledTimes: 1,
      matchDeepInclude: {
        position: {
          ...submitDefaultPosition,
          doorcode: '22key+2',
          entrance: '8B',
          flat: '231556',
          floor: '777',
        },
      },
    })
  })
  it(`yalavka-244: Редактирование адреса, если адрес заполняется впервые. Корректность работы полей адреса`, async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage({
      cookies: {
        ...epsilonOptions.cookies,
        ...makeFutureBackendResponsesCookie({
          'get-address:is_new_address': true,
        }),
      },
    })
    await checkout.waitForCartButtonActive()
    await checkout.scrollToLayoutPageBlock('address', {offsetY: HEADER_SCROLL_COMPENSATION})
    await checkout.assertImage({state: 'page-opened-with-new-address'})
    await checkout.typeTextToAddressField('flat', '666', {clearBefore: true})
    await checkout.typeTextToAddressField('entrance', '1')
    await checkout.typeTextToAddressField('doorcode', '23key+2')
    await checkout.typeTextToAddressField('floor', '888')
    await checkout.assertImage({state: 'address-fields-entered'})
    await checkout.clickAvailablePayButton()
    await waitAndAssertClientRequest(this, 'orders/v2/submit', {
      haveBeenCalledTimes: 1,
      matchDeepInclude: {
        position: {
          ...submitDefaultPosition,
          doorcode: '23key+2',
          entrance: '61',
          flat: '666',
          floor: '888',
        },
      },
    })
  })
  it(`yalavka-244: Информер с уточнением деталей адреса отображается для старого адреса, если не указана квартира`, async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage(epsilonOptions)
    await checkout.scrollToLayoutPageBlock('address', {offsetY: HEADER_SCROLL_COMPENSATION})
    await checkout.waitForCartButtonActive()
    await checkout.waitAndClickAddressField()
    await checkout.waitForDeliveryAddressBottomSheet()
    await checkout.typeAddressBottomSheetAddressFieldText('flat', '', {clearBefore: true})
    await checkout.waitAndClickBottomSheetBackdrop()
    await checkout.assertImage({state: 'clarify-address-informer-showed'})
  })
  /* TODO: после правки https://st.yandex-team.ru/LAVKAFRONT-4708 добавить ещё одни тест (или проверить этот)
     для ручки get-address-v2 (в этом тесте v1) */
  it(`yalavka-245: Смена адреса вручную на чекауте (v1 get-address не находит адрес при выборе) + видно глобальный лоадер`, async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage(epsilonOptions)
    await checkout.scrollToLayoutPageBlock('address', {offsetY: HEADER_SCROLL_COMPENSATION})
    await checkout.waitAndClickAddressField()
    await checkout.waitAndClickAddressFieldFromBottomSheet()
    await checkout.waitForSearchAddressBottomSheet()
    await checkout.waitForFoundItemInSearchBottomSheet({itemNum: 0, textLike: 'Домой'})
    await checkout.assertImage({state: 'search-address-bottom-sheet-opened'})
    await checkout.clickSearchAddressItem(1)
    /* специально в этом сценарии проверим появление и скрытие глобального лоадера, после выбора адреса */
    await checkout.waitForAppLoader()
    await checkout.waitForAppLoader({reverse: true})
    await checkout.waitForDeliveryAddressBottomSheet()
    await checkout.assertImage({state: 'address-selected-and-loaded'})
    await checkout.typeAddressBottomSheetAddressFieldText('flat', '123Б')
    /* специально в этом сценарии чекнем, что при стирании поля, уйдут корректные данные на бек */
    await checkout.typeAddressBottomSheetAddressFieldText('entrance', '', {clearBefore: true})
    await checkout.clickConfirmAddressButton()
    await checkout.clickAvailablePayButton()
    await waitAndAssertClientRequest(this, 'orders/v2/submit', {
      haveBeenCalledTimes: 1,
      matchDeepInclude: {
        position: {
          ...marksistkayaPosition,
          flat: '123Б',
        },
      },
    })
  })
  it(`yalavka-245: Корректность обновления поисковой выдачи при ручном вводе адреса в поле поиска`, async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage({
      cookies: {
        ...epsilonOptions.cookies,
        ...makeFutureBackendResponsesCookie({
          'get-address:is_new_address': true,
        }),
      },
    })
    await checkout.scrollToLayoutPageBlock('address', {offsetY: HEADER_SCROLL_COMPENSATION})
    await checkout.waitAndClickAddressField()
    await checkout.waitForSearchAddressBottomSheet()
    await checkout.typeSearchBottomSheetSearchAddressText('Малые каменщики', {clearBefore: true})
    await checkout.waitForFoundItemInSearchBottomSheet({itemNum: 0, textLike: 'Малые Каменщики'})
    await checkout.assertImage({state: 'address-results-exists'})
    await checkout.clickEraseSearchBottomSheetSearchField()
    await checkout.assertImage({state: 'search-value-remove-clicked'})
    await checkout.typeSearchBottomSheetSearchAddressText('Какой-то адрес')
    await checkout.waitForNotFoundAddressMessageExists()
    await checkout.assertImage({state: 'address-results-are-empty'})
  })
  it(`yalavka-250: Установка чаевых`, async function () {
    const checkout = new CheckoutPage(this)
    await checkout.openPage(epsilonOptions)
    await checkout.waitForCartButtonActive()
    await checkout.scrollToLayoutPageBlock('tips', {offsetY: HEADER_SCROLL_COMPENSATION})
    await checkout.clickTipsVariant('99')
    await checkout.clickSaveTipsCheckbox()
    await checkout.waitForCartButtonActive()
    await checkout.assertImage({state: 'tips-settled'})
    //TODO: написать проверку сохранения чаевых в save/getContext
  })
})
