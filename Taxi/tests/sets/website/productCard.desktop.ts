import { identifiers } from '@lavka/constants'
import { waitAndAssertClientRequest } from '@lavka/tests'

import { API_MAJOR_VERSION } from '../../../src/consts/api'
import { GoodPageDesktop, ProductCard, Upsale } from '../../models'

describe('Мультиплатформа: Карточка товара', function () {
  it('yalavka-145: Открытие карточки товара напрямую по ссылке', async function () {
    const goodPage = new GoodPageDesktop(this)
    await goodPage.openPage({ productId: identifiers.productBase, categoryId: identifiers.categoryBase })
    await goodPage.assertImage({ state: 'page-opened' })
    await goodPage.assertUrlPathname(
      `213/category/${identifiers.categoryBase}/${identifiers.subcategoryBase}/goods/${identifiers.productBase}`,
    )
  })
  /* TODO: после решения задачи LAVKAWEB-708 модалка не открывается, это бага */
  // it('yalavka-146: Добавление товара (адрес не установлен), откроется модалка выбора адреса', async function () {
  //   const goodPage = new GoodPageDesktop(this)
  //   await goodPage.openPage({ productId: identifiers.productBase, categoryId: identifiers.categoryBase })
  //   await goodPage.addToCart({ firstItem: true })
  //   await goodPage.assertImage({ state: 'clicked-add-to-cart' })
  // })
  it('yalavka-146,147,149: Добавление/удаление товара (адрес установлен)', async function () {
    const goodPage = new GoodPageDesktop(this)
    await goodPage.openPage(
      { productId: identifiers.productBase, categoryId: identifiers.categoryBase },
      {
        cookies: {
          lastGeoUri: identifiers.geoPointMarksistskaya,
        },
      },
    )
    await goodPage.addToCart({ firstItem: true })
    await goodPage.waitForHeaderCartButtonLoaded()
    await waitAndAssertClientRequest(this, `/api/v${API_MAJOR_VERSION}/cart/v1/update`, { haveBeenCalledTimes: 1 })
    await goodPage.assertImage({ state: 'item-added-to-cart' })
    await goodPage.addToCart()
    await goodPage.waitForHeaderCartButtonLoaded()
    await waitAndAssertClientRequest(this, `/api/v${API_MAJOR_VERSION}/cart/v1/update`, { haveBeenCalledTimes: 2 })
    await goodPage.assertImage({ state: 'item-added-to-cart-twice' })
    await goodPage.removeFromCart()
    await goodPage.waitForHeaderCartButtonLoaded()
    await goodPage.removeFromCart()
    await waitAndAssertClientRequest(this, '/cart/v1/drop', { haveBeenCalledTimes: 1 })
    await goodPage.assertImage({ state: 'item-removed-from-cart' })
  })
  it('yalavka-238: Отображение товара с бонусами Плюс', async function () {
    const goodPage = new GoodPageDesktop(this)
    await goodPage.openPage({ productId: identifiers.productSigmaWithCashback, categoryId: identifiers.categorySigma })
    await goodPage.assertImage({ state: 'page-opened' })
  })
  it('yalavka-239: Отображение товара со стикерами', async function () {
    const goodPage = new GoodPageDesktop(this)
    await goodPage.openPage({ productId: identifiers.productSigmaWithStickers, categoryId: identifiers.categorySigma })
    await goodPage.assertImage({ state: 'page-opened' })
  })
  it('yalavka-247: Отображение товара со скидкой', async function () {
    const goodPage = new GoodPageDesktop(this)
    await goodPage.openPage({ productId: identifiers.productSigmaWithDiscount, categoryId: identifiers.categorySigma })
    await goodPage.assertImage({ state: 'page-opened' })
  })
  it('yalavka-257: Открытие карточки с апсейлом и клик по товару', async function () {
    const goodPage = new GoodPageDesktop(this)
    const product = new ProductCard(this, { productId: identifiers.productUpsaleBetta })
    const upsale = new Upsale(this)

    await goodPage.openPage({
      productId: identifiers.productSigmaWithSigmaUpsale,
      categoryId: identifiers.categorySigma,
    })
    /* не получается заскринить проскроленную страницу, делаем скрин по всей высоте */
    await goodPage.assertImage({ state: 'page-opened', stretch: true })
    /* кликаем по два раза для проверки корректности */
    await upsale.waitAndClickRightButton()
    await upsale.waitAndClickRightButton()
    await upsale.assertImage({ state: 'clicked-right-upsale-button' })
    await upsale.waitAndClickLeftButton()
    await upsale.waitAndClickLeftButton()
    await upsale.assertImage({ state: 'clicked-left-upsale-button' })
    await product.waitAndClick()
    await goodPage.assertImage({ state: 'second-upsale-product-clicked' })
  })
})
