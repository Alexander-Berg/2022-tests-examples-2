import {identifiers} from '@lavka/constants'
import {makeExperimentsConfigCookies} from '@lavka/tests'

import {MainPage, TrackingPage} from '../../../models'

describe('Custom: Трекинг', async function () {
  it('Страница трекинга загружается, скролл к разным секциям страницы', async function () {
    const tracking = new TrackingPage(this)
    await tracking.openPage({orderId: identifiers.orderSadovnicheskaya})
    await tracking.assertImage({state: 'loaded'})
    await tracking.scrollToPageSection('address')
    await tracking.assertImage({state: 'scrolled-to-address'})
    await tracking.scrollToPageSection('items')
    await tracking.assertImage({state: 'scrolled-to-items'})
    await tracking.scrollToPageSection('summary')
    await tracking.assertImage({state: 'scrolled-to-summary'})
  })

  it('После загрузки страницы трекинга можно вернуться на главную страницу и увидеть заказ', async function () {
    const tracking = new TrackingPage(this)
    const mainPage = new MainPage(this)
    await tracking.openPage({orderId: identifiers.orderSadovnicheskaya})
    await tracking.clickToolbarBackButton()
    await mainPage.waitForPageLoaded()
    await mainPage.assertImage()
  })
  it('При открытии трекинга с неизвестным id заказа, откроется главная страница без заказов', async function () {
    const tracking = new TrackingPage(this)
    const mainPage = new MainPage(this)
    await tracking.openPage({orderId: 'notFoundOrderId', skipWaitForLoading: true})
    await mainPage.waitForPageLoaded()
    await mainPage.assertImage()
  })
  // it('Открытие страницы трекинга с web yandex картой и выключенной отдельной кнопкой назад', async function () {
  //   const tracking = new TrackingPage(this, {useWebMapLayout: true})
  //   const mainPage = new MainPage(this)
  //   await tracking.openPage(
  //     {orderId: identifiers.orderSadovnicheskaya},
  //     {
  //       cookies: {
  //         ...makeExperimentsConfigCookies({
  //           'web-tracking-map': {enabled: true},
  //           tracking_back_button_in_web_map: {enabled: false},
  //         }),
  //       },
  //     },
  //   )
  //   await tracking.waitForMap()
  //   await tracking.assertImage({state: 'page-loaded'})
  //   await tracking.clickToolbarBackButton()
  //   await mainPage.waitForPageLoaded()
  // })
  // it('Открытие страницы трекинга с выключенной нативной и вебной картой', async function () {
  //   const tracking = new TrackingPage(this)
  //   await tracking.openPage(
  //     {orderId: identifiers.orderSadovnicheskaya},
  //     {
  //       cookies: {
  //         cartRetrieveId: identifiers.cartRetrieveEpsilon,
  //         ...makeExperimentsConfigCookies({
  //           'web-tracking-map': {enabled: true},
  //           'disable-tracking-map': {
  //             entities: [
  //               {
  //                 enabled: true,
  //                 countryCodeList: ['RU', 'RUS'],
  //               },
  //             ],
  //           },
  //         }),
  //       },
  //     },
  //   )
  //   await tracking.assertImage()
  // })
})
