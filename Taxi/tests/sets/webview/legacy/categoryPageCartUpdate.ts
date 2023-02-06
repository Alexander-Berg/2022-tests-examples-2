import {baseCategoryId, baseProductId} from '../../../constants/common'
import {addCategoryItemToCart, openCategoryPage, removeCategoryItemFromCart} from '../../../helpers'
import {mkTestId} from '../../../utils/mkTestId'

describe('NO TESTCASE: should correct update cart on category page', async function () {
  it('NO TESTCASE: should add one item to card and check state', async function () {
    await openCategoryPage(this, {categoryId: baseCategoryId})
    await addCategoryItemToCart(this, {productId: baseProductId, firstAddition: true})
    await this.browser.waitForElementExists(mkTestId('cart-button'))
    await this.browser.waitForElementText(mkTestId('cart-button price-text'), '77 ₽')
    await this.browser.assertImage(mkTestId('category-page-layout'))
  })

  it('NO TESTCASE: should add item to card twice check state and remove after', async function () {
    await openCategoryPage(this, {categoryId: baseCategoryId})
    await addCategoryItemToCart(this, {productId: baseProductId, firstAddition: true})
    await addCategoryItemToCart(this, {productId: baseProductId})
    await this.browser.waitForElementExists(mkTestId('cart-button'))
    await this.browser.waitForElementText(mkTestId('cart-button price-text'), '154 ₽')
    await this.browser.assertImage(mkTestId('category-page-layout'), {state: 'item-added-to-cart-twice'})
    await removeCategoryItemFromCart(this, {productId: baseProductId})
    await removeCategoryItemFromCart(this, {productId: baseProductId})
    await this.browser.waitForElementExists(mkTestId('cart-button'), {reverse: true})
    await this.browser.assertImage(mkTestId('category-page-layout'), {state: 'item-removed-from-cart'})
  })
})
