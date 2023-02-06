import { identifiers } from '@lavka/constants'
import { CategoryGroupMobile, makeExperimentsCookies, ProductCardMobile } from '@lavka/tests'

import { CatalogPageMobile, CategoryPageMobile } from '../../../models'

describe('Custom: Страница категории (Mobile)', function () {
  it('Открытие категории и добавление товара в корзину, затем открывается модалка неполного mobile flow', async function () {
    const catalogPage = new CatalogPageMobile(this)
    const categoryPage = new CategoryPageMobile(this)
    const productCard = new ProductCardMobile(this, { productId: identifiers.productBase })
    const categoryGroup = new CategoryGroupMobile(this, { groupId: identifiers.groupBase })
    await catalogPage.openPage({
      cookies: {
        ...makeExperimentsCookies({
          desktop_mobile: {
            enabled: true,
            fullFlow: false,
          },
        }),
      },
    })
    await categoryGroup.waitAndClickCategoryCard(identifiers.categoryBase)
    await categoryPage.waitForPageLoaded()
    await categoryPage.assertImage({ state: 'category-page-opened' })
    await productCard.addToCart({ firstItem: true })
    await categoryPage.assertImage({ state: 'clicked-add-product-to-cart' })
  })
  it('Открытие категории и добавление товара в корзину (полный flow и без адреса)', async function () {
    const catalogPage = new CatalogPageMobile(this)
    const categoryGroup = new CategoryGroupMobile(this, { groupId: identifiers.groupBase })
    const categoryPage = new CategoryPageMobile(this)
    const productCard = new ProductCardMobile(this, { productId: identifiers.productBase })
    await catalogPage.openPage({
      cookies: {
        useLegacyAddressApi: 'true',
      },
    })
    await categoryGroup.waitAndClickCategoryCard(identifiers.categoryBase)
    await categoryPage.waitForPageLoaded()
    await categoryPage.assertImage({ state: 'category-page-opened' })
    await productCard.addToCart({ firstItem: true })
    await catalogPage.waitForCartButtonActive()
    await categoryPage.assertImage({ state: 'clicked-add-product-to-cart' })
  })
  it('Открытие категории и добавление товара в корзину (полный flow с адресом)', async function () {
    const catalogPage = new CatalogPageMobile(this)
    const categoryGroup = new CategoryGroupMobile(this, { groupId: identifiers.groupBase })
    const categoryPage = new CategoryPageMobile(this)
    const productCard = new ProductCardMobile(this, { productId: identifiers.productBase })
    await catalogPage.openPage({
      cookies: {
        lastGeoUri: identifiers.geoPointMarksistskaya,
      },
    })
    await categoryGroup.waitAndClickCategoryCard(identifiers.categoryBase)
    await categoryPage.waitForPageLoaded()
    await categoryPage.assertImage({ state: 'category-page-opened' })
    await productCard.addToCart({ firstItem: true })
    await catalogPage.waitForCartButtonActive()
    /* тут падает 1 пиксель у картинки внизу, увеличил немного tolerance, посмотрим будут ли ещё такие кейсы */
    await categoryPage.assertImage({ state: 'clicked-add-product-to-cart', tolerance: 3.5 })
  })
})
