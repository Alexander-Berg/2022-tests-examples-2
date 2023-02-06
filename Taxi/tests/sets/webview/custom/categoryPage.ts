import {identifiers} from '@lavka/constants'

import {CategoryPage} from '../../../models'

describe('Страница категории', async function () {
  it('Корректное открытие страницы', async function () {
    const categoryPage = new CategoryPage(this)
    await categoryPage.openCategoryPage({categoryId: identifiers.categoryBase})
    await categoryPage.waitForPageLoaded()
  })

  it('Корректное добавление одного товара из сетки', async function () {
    const categoryPage = new CategoryPage(this)
    await categoryPage.openCategoryPage({categoryId: identifiers.categoryBase})
    await categoryPage.addProductToCart(identifiers.productBase, {firstProduct: true})
    await categoryPage.waitForCartButtonActive()
    await categoryPage.waitForCartButtonTextLike('55')
    await categoryPage.assertImage()
  })

  it('Корректное добавление двух товаров из сетки, а затем удаление одного', async function () {
    const categoryPage = new CategoryPage(this)
    await categoryPage.openCategoryPage({categoryId: identifiers.categoryBase})
    await categoryPage.addProductToCart(identifiers.productBase, {firstProduct: true})
    await categoryPage.addProductToCart(identifiers.productBase)
    await categoryPage.waitForCartButtonActive()
    await categoryPage.waitForCartButtonTextLike('110')
    await categoryPage.assertImage({state: 'item-added-to-cart-twice'})
    await categoryPage.removeProductFromCart(identifiers.productBase)
    await categoryPage.removeProductFromCart(identifiers.productBase)
    await categoryPage.waitForCartButtonExists({reverse: true})
    await categoryPage.assertImage({state: 'item-removed-from-cart'})
  })
})
