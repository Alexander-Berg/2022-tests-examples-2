import {identifiers} from '@lavka/constants'
import {makeExperimentsConfigCookies, modifyFutureBackendResponses, waitAndAssertClientRequest} from '@lavka/tests'

import {CheckoutPage, /* CheckoutPage, */ MainPage, TrackingPage} from '../../models'

describe('Трекинг', async function () {
  it('yalavka-118, yalavka-407, yalavka-413: Открытие страницы трекинга с web yandex картой, проверка статусов доставки', async function () {
    const tracking = new TrackingPage(this, {useWebMapLayout: true})
    const mainPage = new MainPage(this)
    await tracking.openPage(
      {orderId: identifiers.orderSadovnicheskaya},
      {
        cookies: {
          ...makeExperimentsConfigCookies({
            'web-tracking-map': {enabled: true},
          }),
        },
      },
    )
    await tracking.assertImage({state: 'page-opened'})
    await tracking.testAllTrackingStatuses()
    await tracking.clickStatusButton()
    await mainPage.waitForPageLoaded()
  })
  it('yalavka-118: Открытие трекинга с некоторыми доп. полями в адресе', async function () {
    const tracking = new TrackingPage(this, {useWebMapLayout: true})
    await tracking.openPage(
      {orderId: identifiers.orderSadovnicheskayaWithMoreAddressFields},
      {
        cookies: {
          ...makeExperimentsConfigCookies({
            'web-tracking-map': {enabled: true},
          }),
        },
      },
    )
    await tracking.clickActionButton('order-details')
    await tracking.scrollToPageSection('address')
    await tracking.assertImage({state: 'page-opened'})
  })
  it('yalavka-118: Открытие трекинга в статусе доставка, и открытие инфы о перевозчике', async function () {
    const tracking = new TrackingPage(this, {useWebMapLayout: true})
    await tracking.openPage(
      {orderId: identifiers.orderSadovnicheskayaWithDriverInfo},
      {
        cookies: {
          ...makeExperimentsConfigCookies({
            'web-tracking-map': {enabled: true},
          }),
        },
      },
    )
    await tracking.clickActionButton('order-details')
    await tracking.scrollToPageSection('address')
    await tracking.assertImage({state: 'supply-info-showed'})
    await tracking.waitAndClickSupplyInfo()
    await tracking.assertImage({state: 'supply-info-clicked'})
    await tracking.waitAndClickBottomSheetBackdrop()
    await tracking.waitForSupplyInfoBottomSheet({reverse: true})
  })
  it('yalavka-411: Заказ падает с ошибкой, возвращается failed статус', async function () {
    const tracking = new TrackingPage(this, {useWebMapLayout: true})
    await tracking.openPage(
      {orderId: identifiers.orderSadovnicheskaya},
      {
        cookies: {
          ...makeExperimentsConfigCookies({
            'web-tracking-map': {enabled: true},
          }),
        },
      },
    )
    await modifyFutureBackendResponses(this, {
      'grocery_orders[0]:status': 'closed',
      'grocery_orders[0]:resolution': 'failed',
    })
    await tracking.waitForStatus('closed')
    await tracking.assertImage({state: 'order-failed'})
  })
  it('yalavka-118: Открытие страницы трекинга, попадаем на главную при клике по кнопке "ещё заказ"', async function () {
    const tracking = new TrackingPage(this, {useWebMapLayout: true})
    const mainPage = new MainPage(this)
    await tracking.openPage(
      {orderId: identifiers.orderSadovnicheskaya},
      {
        cookies: {
          ...makeExperimentsConfigCookies({
            'web-tracking-map': {enabled: true},
          }),
        },
      },
    )
    await tracking.clickActionButton('another-order')
    await mainPage.waitForPageLoaded()
  })
  it('yalavka-118: Открытие страницы трекинга с web yandex картой и раскрытие деталей заказа', async function () {
    const tracking = new TrackingPage(this, {useWebMapLayout: true})
    await tracking.openPage(
      {orderId: identifiers.orderSadovnicheskaya},
      {
        cookies: {
          ...makeExperimentsConfigCookies({
            'web-tracking-map': {enabled: true},
          }),
        },
      },
    )
    await tracking.clickActionButton('order-details')
    await tracking.assertImage({state: 'details-clicked'})
    await tracking.scrollToPageSection('summary')
    await tracking.assertImage({state: 'scrolled-to-summary'})
  })
  it('yalavka-126, yalavka-407, yalavka-413: Открытие страницы трекинга без карты, проверка статусов доставки', async function () {
    const tracking = new TrackingPage(this)
    const mainPage = new MainPage(this)
    await tracking.openPage({orderId: identifiers.orderSadovnicheskaya})
    await tracking.assertImage({state: 'page-opened'})
    await tracking.testAllTrackingStatuses()
    await tracking.clickStatusButton()
    await mainPage.waitForPageLoaded()
  })
  it('yalavka-409, yalavka-410: Ошибка резервирования заказа', async function () {
    const tracking = new TrackingPage(this, {useWebMapLayout: true})
    const checkoutPage = new CheckoutPage(this)
    await tracking.openPage(
      {orderId: identifiers.orderSadovnicheskaya},
      {
        cookies: {
          ...makeExperimentsConfigCookies({
            'web-tracking-map': {enabled: true},
          }),
        },
      },
    )
    await modifyFutureBackendResponses(this, {
      'grocery_orders[0]:status': 'closed',
      'grocery_orders[0]:resolution': 'failed',
      'grocery_orders[0]:payment_status': 'failed',
    })
    await tracking.waitForStatus('closed')
    await tracking.assertImage({state: 'error-reservation-received'})
    await tracking.clickStatusButton()
    await checkoutPage.waitForPageLoaded()
  })
  it('yalavka-406: Отмена заказа клиентом (ошибка отмены)', async function () {
    const tracking = new TrackingPage(this, {useWebMapLayout: true})
    await tracking.openPage(
      {orderId: identifiers.orderSadovnicheskaya},
      {
        cookies: {
          shouldFailCancelOrder: 'true',
          ...makeExperimentsConfigCookies({
            'web-tracking-map': {enabled: true},
          }),
        },
      },
    )
    await tracking.clickCancelOrder()
    await tracking.assertImage({state: 'clicked-cancel-order-button'})
    await tracking.confirmAskCancelOrder()
    await tracking.waitForFailedCancelOrderModal()
    await tracking.assertImage({state: 'clicked-cancel-order-button'})
    await tracking.waitForSuccessCancelOrderModal({reverse: true})
  })
  it('yalavka-406: Отмена заказа клиентом (успех)', async function () {
    const tracking = new TrackingPage(this, {useWebMapLayout: true})
    await tracking.openPage(
      {orderId: identifiers.orderSadovnicheskaya},
      {
        cookies: {
          useCartService: 'true',
          cartRetrieveId: 'cartRetrieveEpsilon',
          ...makeExperimentsConfigCookies({
            'web-tracking-map': {enabled: true},
          }),
        },
      },
    )
    await tracking.clickCancelOrder()
    await tracking.assertImage({state: 'clicked-cancel-order-button'})
    await tracking.confirmAskCancelOrder()
    await waitAndAssertClientRequest(this, 'orders/v1/actions/cancel', {haveBeenCalledTimes: 1})
    await waitAndAssertClientRequest(this, 'cart/v1/restore', {
      haveBeenCalledTimes: 1,
      calledAfter: ['orders/v1/actions/cancel', {haveBeenCalledTimes: 1}],
    })
    await waitAndAssertClientRequest(this, 'cart/v1/set-cashback-flow', {
      haveBeenCalledTimes: 1,
      calledAfter: ['cart/v1/restore', {haveBeenCalledTimes: 1}],
    })
    await tracking.waitForSuccessCancelOrderModal()
    await tracking.assertImage({state: 'showed-success-cancel-order-modal'})
    await tracking.confirmSuccessCancelOrder()
    await tracking.waitForSuccessCancelOrderModal({reverse: true})
  })
})
