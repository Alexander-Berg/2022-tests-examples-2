import { identifiers } from '@lavka/constants'
import { ProductCardMobile, waitAndAssertClientRequest } from '@lavka/tests'

import { API_MAJOR_VERSION } from '../../../../src/consts/api'
import { GoodPageMobile } from '../../../models'

describe('Custom: Карточка товара (Mobile)', function () {
  it('Открытие карточки товара напрямую по ссылке', async function () {
    const goodPage = new GoodPageMobile(this)
    await goodPage.openPage({ productId: identifiers.productBase, categoryId: identifiers.categoryBase })
    await goodPage.assertImage({ state: 'page-opened' })
    await goodPage.assertUrlPathname(
      `213/category/${identifiers.categoryBase}/${identifiers.subcategoryBase}/goods/${identifiers.productBase}`,
    )
  })
  /* TODO: после решения задачи LAVKAWEB-708 модалка не открывается, это бага */
  // it('Добавление товара (адрес не установлен), откроется модалка выбора адреса', async function () {
  //   const goodPage = new GoodPageMobile(this)
  //   await goodPage.openPage({ productId: identifiers.productBase, categoryId: identifiers.categoryBase })
  //   await goodPage.addToCart({ firstItem: true })
  //   await goodPage.assertImage({ state: 'clicked-add-to-cart' })
  // })
  it('Добавление/удаление товара (адрес установлен)', async function () {
    const goodPage = new GoodPageMobile(this)
    await goodPage.openPage(
      { productId: identifiers.productBase, categoryId: identifiers.categoryBase },
      {
        cookies: {
          lastGeoUri: identifiers.geoPointMarksistskaya,
        },
      },
    )
    await goodPage.addToCart({ firstItem: true })
    await goodPage.waitForCartButtonActive()
    await waitAndAssertClientRequest(this, `/api/v${API_MAJOR_VERSION}/cart/v1/update`, { haveBeenCalledTimes: 1 })
    await goodPage.assertImage({ state: 'item-added-to-cart', tolerance: 3.5 })
    await goodPage.addToCart()
    await goodPage.waitForCartButtonActive()
    await waitAndAssertClientRequest(this, `/api/v${API_MAJOR_VERSION}/cart/v1/update`, { haveBeenCalledTimes: 2 })
    await goodPage.assertImage({ state: 'item-added-to-cart-twice', tolerance: 3.5 })
    await goodPage.removeFromCart()
    await goodPage.waitForCartButtonActive()
    await goodPage.removeFromCart()
    await waitAndAssertClientRequest(this, '/cart/v1/drop', { haveBeenCalledTimes: 1 })
    await goodPage.assertImage({ state: 'item-removed-from-cart', tolerance: 3.5 })
  })
  it('Отображение товара с бонусами Плюс', async function () {
    const goodPage = new GoodPageMobile(this)
    await goodPage.openPage({ productId: identifiers.productSigmaWithCashback, categoryId: identifiers.categorySigma })
    await goodPage.assertImage({ state: 'page-opened' })
  })
  it('Отображение товара со стикерами', async function () {
    const goodPage = new GoodPageMobile(this)
    await goodPage.openPage({ productId: identifiers.productSigmaWithStickers, categoryId: identifiers.categorySigma })
    await goodPage.assertImage({ state: 'page-opened' })
  })
  it('Отображение товара со скидкой', async function () {
    const goodPage = new GoodPageMobile(this)
    await goodPage.openPage({ productId: identifiers.productSigmaWithDiscount, categoryId: identifiers.categorySigma })
    await goodPage.assertImage({ state: 'page-opened' })
  })
  it('Открытие карточки с апсейлом и клик по товару', async function () {
    const goodPage = new GoodPageMobile(this)
    const product = new ProductCardMobile(this, { productId: identifiers.productUpsaleBetta })
    await goodPage.openPage({
      productId: identifiers.productSigmaWithSigmaUpsale,
      categoryId: identifiers.categorySigma,
    })
    await goodPage.assertImage({ state: 'product-opened', stretch: true })
    await product.waitAndClick()
    await goodPage.assertImage({ state: 'second-upsale-product-clicked' })
  })
  it('Открытие карточки товара с несуществующей категорией', async function () {
    const goodPage = new GoodPageMobile(this)
    await goodPage.openPage({ productId: identifiers.productBase, categoryId: 'unknown' })
    await goodPage.assertUrlPathname(`213/good/${identifiers.productBase}`)
  })
  it('Отображение товара без картинки', async function () {
    const goodPage = new GoodPageMobile(this)
    await goodPage.openPage({ productId: identifiers.productSigmaNoImage, categoryId: identifiers.categorySigma })
    await goodPage.assertImage({ state: 'page-opened' })
  })
  it('Отображение несуществующего товара', async function () {
    const goodPage = new GoodPageMobile(this)
    await goodPage.openPage({ productId: 'unknown', categoryId: identifiers.categorySigma, waitForLoaded: false })
    await goodPage.waitForUnavailablePlaceholder()
    await goodPage.assertImage({ state: 'page-opened' })
  })
})
