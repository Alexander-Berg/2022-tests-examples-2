import {makeExperimentsCookies} from '@lavka/tests'

import {HourSlotsCheckoutPage, MainPage, OneClickCheckoutPage} from '../../../models'

describe('Parcels: Посылки', async function () {
  const alphaPackagesOptions = {
    cookies: {
      packagesId: 'alphaPackagesId',
      useCartService: 'true',
      cartRetrieveId: 'cartRetrieveParcel1',
      ...makeExperimentsCookies({'lavka-frontend_web-payment-method': {paymentsWithCartBindingEnabled: true}}),
    },
  }

  const betaPackagesOptions = {
    cookies: {
      packagesId: 'betaPackagesId',
    },
  }

  it('На главной есть модалка', async function () {
    const mainPage = new MainPage(this)
    await mainPage.openPage(alphaPackagesOptions)
    await mainPage.waitForMarketPackageModal()
    await mainPage.waitForCartButtonActive()
    await mainPage.assertImage({
      state: 'packages-modal-opened',
    })
  })

  it('Можно открыть Ванклик', async function () {
    const page = new OneClickCheckoutPage(this)
    await page.openPage({packageOrder: 'alphaOrderRef'}, alphaPackagesOptions)
    await page.waitForPageLoaded()
    await page.waitForUpsaleLoaded()
    await page.waitForCartButtonActive()
    // TODO: use wait for image
    await this.browser.pause(5000)
    await page.assertImage({
      state: 'page-opened',
    })
  })

  it('Можно открыть Ванклик и добавить товар из апсейла', async function () {
    const page = new OneClickCheckoutPage(this)
    await page.openPage({packageOrder: 'alphaOrderRef'}, alphaPackagesOptions)
    await page.waitForPageLoaded()
    await page.waitForUpsaleLoaded()
    await page.assertPageItemSubtitle('№alphaOrderRef')
    const upsale = page.getUpsale()
    await upsale.scrollToUpsale()
    await upsale.clickAddProductToCart('product-id-upsaleAlphaProduct')
    await page.waitForCartButtonActive({loading: true})
    await page.waitForCartButtonActive()
    await page.assertPageItemSubtitle('№alphaOrderRef. и 1 товар из Лавки')
    await page.assertImage({
      state: 'add-item-from-upsale',
    })
  })

  it('Можно открыть экран часовых слотов', async function () {
    const page = new HourSlotsCheckoutPage(this)
    await page.openPage({packageOrder: 'betaOrderRef'}, betaPackagesOptions)
    await page.waitForPageLoaded()
    await page.waitForCartButtonActive()
    await page.assertImage({
      state: 'page-opened',
    })
  })
})
