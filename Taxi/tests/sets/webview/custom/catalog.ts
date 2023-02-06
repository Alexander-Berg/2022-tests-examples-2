import {identifiers} from '@lavka/constants'

import {CategoryPage, CartPage} from '../../../models'

describe('Страница корзины', async function () {
  it('Верное отображение скидки продукта при открытии категории, затем обновление корзины, которая не пришлёт скидку', async function () {
    const categoryPage = new CategoryPage(this)
    const cartPage = new CartPage(this)
    await categoryPage.openCategoryPage(
      {categoryId: identifiers.categoryWithSomeProductDiscount},
      {
        cookies: {
          cartRetrieveId: identifiers.gammaCartRetrieve,
          useCartService: 'true',
        },
      },
    )
    await categoryPage.waitForCartButtonActive()
    await categoryPage.assertImage({state: 'category-opened'})
    await categoryPage.addProductToCart(identifiers.productWithDiscount)
    await categoryPage.waitForCartButtonActive()
    await categoryPage.assertImage({state: 'cart-response-got-without-discount'})
    await categoryPage.waitAndClickCartButton()
    await cartPage.waitForPageLoaded()
    await categoryPage.waitForCartButtonActive()
    await cartPage.assertImage({state: 'opened-cart-page'})
  })
})
