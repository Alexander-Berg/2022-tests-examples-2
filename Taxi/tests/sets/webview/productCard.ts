import {
  baseCategoryId,
  baseProductId,
  sigmaCategoryId,
  sigmaProductWithCashbackId,
  sigmaProductWithDiscountId,
  sigmaProductWithStickersId,
  sigmaProductWithUpsaleId,
  sigmaProductWithInformersId,
  sigmaProductNoImageId,
  sigmaProductExpiringId,
  sigmaProductWithGradesId,
} from '../../constants/common'
import {categoryProductItemClick} from '../../helpers'
import {mkTestId} from '../../utils/mkTestId'

/* Testcases: https://nda.ya.ru/t/Ld6ZRH4w4mk6sr */
describe('Мультиплатформа: Карточка товара', async function () {
  const baseCategoryPageUrl = `/?group=0f1846f41ac8453680a175023a77fae3&category=${baseCategoryId}`
  const sigmaCategoryPageUrl = `/?group=0f1846f41ac8453680a175023a77fae3&category=${sigmaCategoryId}`

  it('Мультиплатформа: Открытие простой карточки товара', async function () {
    await this.browser.openPage(baseCategoryPageUrl)
    await categoryProductItemClick(this, {productId: baseProductId})
    await this.browser.waitForElementExists(mkTestId('product-card-bottom-sheet'))
    await this.browser.assertImage(mkTestId('product-card-bottom-sheet'))
  })
  it('Мультиплатформа: Карточка товара - добавление товара в корзину', async function () {
    await this.browser.openPage(baseCategoryPageUrl)
    await categoryProductItemClick(this, {productId: baseProductId})
    await this.browser.waitForElementExists(mkTestId('product-card-bottom-sheet'))
    await this.browser.waitForElementAndClick(mkTestId('add-to-cart-bar product-add'))
    // Ожидаем новое значение цены на кнопке, так как оно вернётся асинхронно позже
    await this.browser.waitForElementText(mkTestId('cart-button price-text'), '77 ₽')
    await this.browser.assertImage(mkTestId('product-card-bottom-sheet'))
  })
  it('Мультиплатформа: Карточка товара - изменение количества товара в корзине', async function () {
    await this.browser.openPage(baseCategoryPageUrl)
    await categoryProductItemClick(this, {productId: baseProductId})
    await this.browser.waitForElementExists(mkTestId('product-card-bottom-sheet'))
    await this.browser.waitForElementAndClick(mkTestId('add-to-cart-bar product-add'))
    await this.browser.waitForElementExists(mkTestId('cart-button'))
    await this.browser.waitForElementAndClick(mkTestId('add-to-cart-bar add-spin-button'))
    await this.browser.waitForElementText(mkTestId('cart-button price-text'), '154 ₽')
    await this.browser.assertImage(mkTestId('product-card-bottom-sheet'))
  })
  it('Мультиплатформа: Карточка товара - удаление товара из корзины', async function () {
    await this.browser.openPage(baseCategoryPageUrl)
    await categoryProductItemClick(this, {productId: baseProductId})
    await this.browser.waitForElementExists(mkTestId('product-card-bottom-sheet'))
    await this.browser.waitForElementAndClick(mkTestId('add-to-cart-bar product-add'))
    await this.browser.waitForElementExists(mkTestId('cart-button'))
    await this.browser.waitForElementAndClick(mkTestId('add-to-cart-bar remove-spin-button'))
    await this.browser.waitForElementExists(mkTestId('cart-button'), {reverse: true})
    await this.browser.assertImage(mkTestId('product-card-bottom-sheet'))
  })
  it('Мультиплатформа: Карточка товара - отображение карточки товара с бонусами Плюс', async function () {
    await this.browser.openPage(sigmaCategoryPageUrl)
    await categoryProductItemClick(this, {productId: sigmaProductWithCashbackId})
    await this.browser.waitForElementExists(mkTestId('product-card-bottom-sheet'))
    await this.browser.assertImage(mkTestId('product-card-bottom-sheet'))
  })
  it('Мультиплатформа: Карточка товара - отображение стикеров', async function () {
    await this.browser.openPage(sigmaCategoryPageUrl)
    await categoryProductItemClick(this, {productId: sigmaProductWithStickersId})
    await this.browser.waitForElementExists(mkTestId('product-card-bottom-sheet'))
    await this.browser.assertImage(mkTestId('product-card-bottom-sheet'))
  })
  it('Мультиплатформа: Карточка товара - отображение информеров', async function () {
    await this.browser.openPage(sigmaCategoryPageUrl)
    await categoryProductItemClick(this, {productId: sigmaProductWithInformersId})
    await this.browser.waitForElementExists(mkTestId('product-card-bottom-sheet'))
    await this.browser.assertImage(mkTestId('product-card-bottom-sheet'))
  })
  it('Мультиплатформа: Карточка товара - без картинки', async function () {
    await this.browser.openPage(sigmaCategoryPageUrl)
    await categoryProductItemClick(this, {productId: sigmaProductNoImageId})
    await this.browser.waitForElementExists(mkTestId('product-card-bottom-sheet'))
    await this.browser.assertImage(mkTestId('product-card-bottom-sheet'))
  })
  it('Мультиплатформа: Карточка товара - товар с истекающим сроком годности', async function () {
    await this.browser.openPage(sigmaCategoryPageUrl)
    await categoryProductItemClick(this, {productId: sigmaProductExpiringId})
    await this.browser.waitForElementExists(mkTestId('product-card-bottom-sheet'))
    await this.browser.assertImage(mkTestId('product-card-bottom-sheet'))
  })
  it('Мультиплатформа: Карточка товара - весовой товар', async function () {
    await this.browser.openPage(sigmaCategoryPageUrl)
    await categoryProductItemClick(this, {productId: sigmaProductWithGradesId})
    await this.browser.waitForElementExists(mkTestId('product-card-bottom-sheet'))
    await this.browser.assertImage(mkTestId('product-card-bottom-sheet'))
  })
  it('Мультиплатформа: Карточка товара - отображение товара со скидкой', async function () {
    await this.browser.openPage(sigmaCategoryPageUrl)
    await categoryProductItemClick(this, {productId: sigmaProductWithDiscountId})
    await this.browser.waitForElementExists(mkTestId('product-card-bottom-sheet'))
    await this.browser.assertImage(mkTestId('product-card-bottom-sheet'))
  })
  it('Мультиплатформа: Карточка товара - открытие карточки с апсейлом', async function () {
    await this.browser.openPage(sigmaCategoryPageUrl)
    await categoryProductItemClick(this, {productId: sigmaProductWithUpsaleId})
    await this.browser.waitForElementExists(mkTestId('product-card-bottom-sheet'))
    await this.browser.waitForElementExists(mkTestId('item-details-toast'))
    await this.browser.assertImage(mkTestId('product-card-bottom-sheet'))
  })
  it('Мультиплатформа: Карточка товара - отображение с доскроллированием до апсейла', async function () {
    await this.browser.openPage(sigmaCategoryPageUrl)
    await categoryProductItemClick(this, {productId: sigmaProductWithUpsaleId})
    await this.browser.waitForElementExists(mkTestId('product-card-bottom-sheet'))
    await this.browser.scrollToElement(mkTestId('product-upsale'))
    await this.browser.waitForElementExists(mkTestId('item-details-toast'))
    await this.browser.assertImage(mkTestId('product-card-bottom-sheet'), {state: 'scrolled-to-upsale'})
    await this.browser.scrollToElementEdge(
      mkTestId('product-card-bottom-sheet product-upsale horizontal-scrollable-container'),
      {
        direction: 'right',
      },
    )
    await this.browser.assertImage(mkTestId('product-card-bottom-sheet'), {state: 'upsale-scrolled-right'})
  })
  it(`Мультиплатформа: Карточка товара - клип по баблу 'Подробнее о товаре' перемещает скролл вниз к описанию товара`, async function () {
    await this.browser.openPage(sigmaCategoryPageUrl)
    await categoryProductItemClick(this, {productId: sigmaProductWithUpsaleId})
    await this.browser.waitForElementExists(mkTestId('product-card-bottom-sheet'))
    await this.browser.waitForElementAndClick(mkTestId('item-details-toast'))
    await this.browser.waitForElementScrollReleased(mkTestId('bottom-sheet-body'))
    await this.browser.assertImage(mkTestId('product-card-bottom-sheet'))
  })
  it('Мультиплатформа: Карточка товара - добавление товара в корзину из апсейла', async function () {
    const productCardInUpsaleSelector = 'product-upsale product-id-upsaleAlphaProduct'
    await this.browser.openPage(sigmaCategoryPageUrl)
    await categoryProductItemClick(this, {productId: sigmaProductWithUpsaleId})
    await this.browser.waitForElementExists(mkTestId('product-card-bottom-sheet'))
    await this.browser.scrollToElement(mkTestId('product-upsale'))
    await this.browser.waitForElementAndClick(mkTestId(`${productCardInUpsaleSelector} product-card-add-button`))
    await this.browser.waitForElementExists(mkTestId('cart-button'))
    await this.browser.waitForElementExists(mkTestId('item-details-toast'))
    await this.browser.assertImage(mkTestId('product-card-bottom-sheet'))
  })
  it('Мультиплатформа: Карточка товара - редактирование количества добавленного в корзину товара из апсейла', async function () {
    const productCardInUpsaleSelector = 'product-upsale product-id-upsaleAlphaProduct'
    await this.browser.openPage(sigmaCategoryPageUrl)
    await categoryProductItemClick(this, {productId: sigmaProductWithUpsaleId})
    await this.browser.waitForElementExists(mkTestId('product-card-bottom-sheet'))
    await this.browser.scrollToElement(mkTestId('product-upsale'))
    await this.browser.waitForElementAndClick(mkTestId(`${productCardInUpsaleSelector} product-card-add-button`))
    await this.browser.waitForElementAndClick(mkTestId(`${productCardInUpsaleSelector} add-spin-button`))
    await this.browser.waitForElementText(mkTestId('cart-button price-text'), '154 ₽')
    await this.browser.waitForElementExists(mkTestId('item-details-toast'))
    await this.browser.assertImage(mkTestId('product-card-bottom-sheet'), {state: 'item-added-to-cart-twice'})
    await this.browser.waitForElementAndClick(mkTestId(`${productCardInUpsaleSelector} remove-spin-button`))
    await this.browser.waitForElementText(mkTestId('cart-button price-text'), '77 ₽')
    await this.browser.assertImage(mkTestId('product-card-bottom-sheet'), {state: 'one-item-removed'})
  })
})
