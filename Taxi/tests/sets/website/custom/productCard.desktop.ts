import { identifiers } from '@lavka/constants'

import { CategoryPageDesktop, ProductCard, GoodPageDesktop } from '../../../models'

describe('Custom: Карточка товара', function () {
  it('Открытие карточки товара со страницы категории', async function () {
    const categoryPage = new CategoryPageDesktop(this)
    const product = new ProductCard(this, { productId: identifiers.productBase })
    const goodPage = new GoodPageDesktop(this)
    await categoryPage.openPage(identifiers.categoryBase)
    await product.waitAndClick()
    await goodPage.assertImage({ state: 'product-page-opened', stretch: true })
    await goodPage.assertUrlPathname(
      `213/category/${identifiers.categoryBase}/${identifiers.subcategoryBase}/goods/${identifiers.productBase}`,
    )
  })
  it('Открытие карточки товара с несуществующей категорией', async function () {
    const goodPage = new GoodPageDesktop(this)
    await goodPage.openPage({ productId: identifiers.productBase, categoryId: 'unknown' })
    await goodPage.assertUrlPathname(`213/good/${identifiers.productBase}`)
  })
  it('Отображение товара без картинки', async function () {
    const goodPage = new GoodPageDesktop(this)
    await goodPage.openPage({ productId: identifiers.productSigmaNoImage, categoryId: identifiers.categorySigma })
    await goodPage.assertImage({ state: 'page-opened' })
  })
  it('Отображение несуществующего товара', async function () {
    const goodPage = new GoodPageDesktop(this)
    await goodPage.openPage({ productId: 'unknown', categoryId: identifiers.categorySigma, waitForLoaded: false })
    await goodPage.waitForUnavailablePlaceholder()
    await goodPage.assertImage({ state: 'page-opened' })
  })
})
