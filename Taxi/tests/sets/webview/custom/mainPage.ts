import {identifiers} from '@lavka/constants'

import {MainPage} from '../../../models'

describe('Главная страница', async function () {
  it('Корректное открытие страницы', async function () {
    const page = new MainPage(this)
    await page.openPage()
    await page.waitForPageLoaded()
    await page.assertImage()
  })

  it('Можно открытию категорию и затем вернуться обратно', async function () {
    const page = new MainPage(this)
    await page.openPage()
    await page.waitAndClickForCategoryCard(identifiers.categoryBase)
    await page.waitAndClickBackNavigationButton()
    await page.assertImage()
  })
})
