// TODO: сделать абсолютные импорты https://st.yandex-team.ru/LAVKAFRONT-4906

import { identifiers } from '@lavka/constants'
import { waitAndAssertClientRequest } from '@lavka/tests'

import { API_MAJOR_VERSION } from '../../../src/consts/api'
import { CategoryPageDesktop, ProductCard } from '../../models'

describe('Страница категории', function () {
  /* TODO: для yalavka-172 в задаче LAVKAWEB-708 модалка не открывается */
  // it('yalavka-172: открывается модалка адреса при клике "в корзине" (адрес не выбран)', async function () {
  //   const categoryPage = new CategoryPageDesktop(this)
  //   const product = new ProductCard(this, { productId: identifiers.productBase })
  //   await categoryPage.openPage(identifiers.categoryBase)
  //   await product.addToCart({ firstItem: true })
  //   await categoryPage.assertImage({ state: 'product-add-cart-clicked' })
  // })

  it('yalavka-172, yalavka-174, yalavka-175: добавление/удаление товара в корзине из каталога (адрес выбран)', async function () {
    const categoryPage = new CategoryPageDesktop(this)
    const product = new ProductCard(this, { productId: identifiers.productBase })
    await categoryPage.openPage(identifiers.categoryBase, {
      cookies: {
        lastGeoUri: identifiers.geoPointMarksistskaya,
      },
    })
    await product.addToCart({ firstItem: true })
    await categoryPage.waitForSideCartButtonLoaded()
    await waitAndAssertClientRequest(this, `/api/v${API_MAJOR_VERSION}/cart/v1/update`, { haveBeenCalledTimes: 1 })
    await categoryPage.assertImage({ state: 'product-added-to-cart' })
    await product.addToCart()
    await categoryPage.waitForSideCartButtonLoaded()
    await waitAndAssertClientRequest(this, `/api/v${API_MAJOR_VERSION}/cart/v1/update`, { haveBeenCalledTimes: 2 })
    await categoryPage.assertImage({ state: 'product-added-to-cart-twice' })
    await product.removeProduct()
    await categoryPage.waitForSideCartButtonLoaded()
    await waitAndAssertClientRequest(this, `/api/v${API_MAJOR_VERSION}/cart/v1/update`, { haveBeenCalledTimes: 3 })
    await categoryPage.assertImage({ state: 'product-removed-from-cart' })
    await product.removeProduct()
    await categoryPage.waitForSideCartButtonLoaded()
    await waitAndAssertClientRequest(this, `/api/v${API_MAJOR_VERSION}/cart/v1/drop`, { haveBeenCalledTimes: 1 })
    await categoryPage.assertImage({ state: 'product-removed-from-cart-via-counter' })
  })
})
