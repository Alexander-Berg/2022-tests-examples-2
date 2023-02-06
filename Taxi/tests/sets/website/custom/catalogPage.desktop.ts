// TODO: сделать абсолютные импорты https://st.yandex-team.ru/LAVKAFRONT-4906

import { identifiers } from '@lavka/constants'

import { CatalogPageDesktop, CategoryPageDesktop, CategoryTile } from '../../../models'

describe('Custom: Каталог', function () {
  it('Открытие главной страницы (без адреса)', async function () {
    const catalogPage = new CatalogPageDesktop(this)
    await catalogPage.openPage({
      cookies: {
        useLegacyAddressApi: 'true',
      },
    })
    await catalogPage.assertImage({ state: 'page-opened' })
  })
  it('Открытие каталога с выбранным адресом по last geo точке', async function () {
    const catalogPage = new CatalogPageDesktop(this)
    await catalogPage.openPage({
      cookies: {
        lastGeoUri: identifiers.geoPointMarksistskaya,
      },
    })
    await catalogPage.assertImage({ state: 'page-opened-with-last-geo-address' })
  })
  it('Открытие категории через главную страницу и возврат назад в каталог через нативный back', async function () {
    const catalogPage = new CatalogPageDesktop(this)
    const categoryTile = new CategoryTile(this, { categoryId: identifiers.categoryBase })
    const categoryPage = new CategoryPageDesktop(this)
    await catalogPage.openPage()
    await categoryTile.waitAndClick()
    await categoryPage.waitForPageLoaded()
    await categoryPage.assertImage({ state: 'category-page-opened' })
    await categoryPage.back()
    await categoryPage.assertImage({ state: 'returned-to-catalog' })
  })
  it('Открытие сетки товаров с разным и большим количеством категорий', async function () {
    const catalogPage = new CatalogPageDesktop(this)
    await catalogPage.openPage({
      cookies: {
        layoutId: identifiers.layoutDeltaId,
      },
    })
    await catalogPage.assertImage({ state: 'page-opened', stretch: true })
  })
})
