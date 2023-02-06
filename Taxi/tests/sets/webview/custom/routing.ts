import {expect} from 'chai'

import {makeExperimentsConfigCookies} from '@lavka/tests'

import {CategoryPage, MainPage, OneClickCheckoutPage} from '../../../models'

describe('Routing: Корректное поведение сценариев при роутинге', async function () {
  const deltaLayoutGridOptions = {
    cookies: {
      layoutId: 'routerLayoutId',
    },
  }

  /* Этот тест не может проверить кратковременное мелькание скролла на неверной позиции */
  it('Проверка, что скролл подкатегории, не влияет на скролл главной страницы при возврате назад', async function () {
    const mainPage = new MainPage(this)
    const categoryPage = new CategoryPage(this)
    await mainPage.openPage(deltaLayoutGridOptions)
    await mainPage.waitAndClickForCategoryCard('routerCategoryId-0')
    await categoryPage.waitForPageLoaded()
    await categoryPage.scrollBodyToEdge({direction: 'down'})
    await categoryPage.waitForPageScrollReleased()
    await categoryPage.waitAndClickBackNavigationButton()
    await mainPage.waitForPageLoaded()
    await mainPage.assertImage()
  })
  it('Проверка, что открывается верная страница (доставка по клику), если в url есть двойной слэш', async function () {
    const oneClickPage = new OneClickCheckoutPage(this)
    /* открываем без посылки, так как нам важно только открытие */
    await oneClickPage.open('//one-click-checkout', {
      cookies: {
        ...makeExperimentsConfigCookies({'lavka-frontend_fix-url-double-slash': {enabled: true}}),
      },
    })
    await oneClickPage.waitForPageLoaded()
    await oneClickPage.waitForUpsaleLoaded()
    await oneClickPage.waitForCartButtonActive({reverse: true})
    const url = new URL(await this.browser.getUrl())
    expect(url.pathname).does.not.include('//')
    await oneClickPage.assertImage()
  })
})
