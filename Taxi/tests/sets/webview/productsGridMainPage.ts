import {mkDataId, mkTestId} from '../../utils/mkTestId'

describe('Сетка товаров. Главная страница.', async function () {
  const deltaLayoutGridOptions = {
    cookies: {
      layoutId: 'deltaLayoutId',
    },
  }

  const categoryGroupAdult18Selector = `${mkTestId('category-group')}${mkDataId(
    'deltaGroupCarouselWithRestrictionsAdult18Id',
  )}`
  const firstProductInCarouselAdult18Selector = `${categoryGroupAdult18Selector} ${mkTestId(
    'product-id-deltaProductWithRestrictionsAdult18Id-0',
  )}`
  const adultModal = `${mkTestId('modal')} [data-modal-id="adult-modal"]`

  it('Корректное отображение страницы без прокрутки', async function () {
    await this.browser.openPage('/', deltaLayoutGridOptions)
    await this.browser.waitForElementExists(mkTestId('main-page-layout'))
    await this.browser.assertImage(mkTestId('main-page-layout'))
  })
  it('Корректное отображение, когда прокрутили к верхней группе', async function () {
    const categoryGroupSelector = `${mkTestId('category-group')}[data-id="deltaGroupId-topGroup"]`
    await this.browser.openPage('/', deltaLayoutGridOptions)
    await this.browser.waitForElementExists(categoryGroupSelector)
    await this.browser.scrollToElement(categoryGroupSelector, {offsetY: -80})
    await this.browser.assertImage(mkTestId('main-page-layout'))
  })
  it('Корректное отображение, когда прокрутили к группе карусели', async function () {
    const categoryGroupSelector = `${mkTestId('category-group')}[data-id="deltaGroupCarouselId"]`
    await this.browser.openPage('/', deltaLayoutGridOptions)
    await this.browser.waitForElementExists(categoryGroupSelector)
    await this.browser.scrollToElement(categoryGroupSelector, {offsetY: -80})
    await this.browser.assertImage(mkTestId('main-page-layout'))
  })
  it('Корректное отображение, когда прокрутили к группе после карусели', async function () {
    const categoryGroupSelector = `${mkTestId('category-group')}[data-id="deltaGroupId-bottomGroups-0"]`
    await this.browser.openPage('/', deltaLayoutGridOptions)
    await this.browser.waitForElementExists(categoryGroupSelector)
    await this.browser.scrollToElement(categoryGroupSelector, {offsetY: -80})
    await this.browser.assertImage(mkTestId('main-page-layout'))
  })
  it('Корректное отображение, когда прокрутили страницу вниз и вверх до упора', async function () {
    await this.browser.openPage('/', deltaLayoutGridOptions)
    await this.browser.waitForElementExists(mkTestId('main-page-layout'))
    await this.browser.scrollToElementEdge('body')
    await this.browser.assertImage(mkTestId('main-page-layout'), {state: 'scrolled-to-bottom'})
    await this.browser.scrollToElementEdge('body', {direction: 'up'})
    await this.browser.assertImage(mkTestId('main-page-layout'), {state: 'scrolled-to-up'})
  })
  it('Карусель категории. Корректная прокрутка и отображение аплифта вправо и обратно до упора', async function () {
    const categoryGroupSelector = `${mkTestId('category-group')}[data-id="deltaGroupCarouselId"]`
    const categoryGroupScrollableSelector = `${categoryGroupSelector} ${mkTestId('horizontal-scrollable-container')}`
    await this.browser.openPage('/', deltaLayoutGridOptions)
    await this.browser.waitForElementExists(categoryGroupSelector)
    await this.browser.scrollToElement(categoryGroupSelector, {offsetY: -80})
    await this.browser.scrollToElementEdge(categoryGroupScrollableSelector, {direction: 'right'})
    await this.browser.assertImage(mkTestId('main-page-layout'), {state: 'uplift-scrolled-to-right'})
    await this.browser.scrollToElementEdge(categoryGroupScrollableSelector, {direction: 'left'})
    await this.browser.assertImage(mkTestId('main-page-layout'), {state: 'uplift-scrolled-to-left'})
  })
  it(`Карусель категории. При нажатии из аплифта на 'Все' открывается его категория`, async function () {
    const categoryGroupSelector = `${mkTestId('category-group')}[data-id="deltaGroupCarouselId"]`
    await this.browser.openPage('/', deltaLayoutGridOptions)
    await this.browser.waitForElementAndClick(`${categoryGroupSelector} ${mkTestId('all-button')}`)
    await this.browser.waitForElementExists(mkTestId('category-page-layout'))
  })
  it(`Карусель категории. При нажатии из аплифта на 'Смотреть все' открывается его категория`, async function () {
    const categoryGroupSelector = `${mkTestId('category-group')}[data-id="deltaGroupCarouselId"]`
    const categoryGroupScrollableSelector = `${categoryGroupSelector} ${mkTestId('horizontal-scrollable-container')}`
    await this.browser.openPage('/', deltaLayoutGridOptions)
    await this.browser.waitForElementExists(categoryGroupSelector)
    await this.browser.scrollToElementEdge(categoryGroupScrollableSelector, {direction: 'right'})
    await this.browser.waitForElementAndClick(`${categoryGroupSelector} ${mkTestId('more-button')}`)
    await this.browser.waitForElementExists(mkTestId('category-page-layout'))
  })
  it(`Информеры. Корректность отображения и функционала информера с модалкой из service-info`, async function () {
    const informerSelector = `${mkTestId('promo-informer')}${mkDataId(
      'lavka-frontend_informers__deltaPromoInformer-1',
    )}`

    const informerBackButton = `${mkTestId('informer-modal')} ${mkTestId('action-button')}[data-action-id="unset"]`
    const informerLinkButton = `${mkTestId('informer-modal')} ${mkTestId('action-button')}[data-action-id="link"]`

    await this.browser.openPage('/', deltaLayoutGridOptions)
    await this.browser.waitForElementExists(informerSelector)
    await this.browser.scrollToElement(informerSelector, {offsetY: -80})
    await this.browser.assertImage(mkTestId('main-page-layout'), {state: 'informer-viewed'})
    await this.browser.waitForElementAndClick(informerSelector)
    await this.browser.assertImage(mkTestId('main-page-layout'), {state: 'informer-modal-viewed'})
    await this.browser.waitForElementAndClick(informerBackButton)
    await this.browser.assertImage(mkTestId('main-page-layout'), {state: 'informer-modal-closed-via-back-button'})
    await this.browser.waitForElementAndClick(informerSelector)
    await this.browser.waitForElementAndClick(informerLinkButton)
    await this.browser.waitForElementExists(mkTestId('category-page-layout'))
  })
  it(`Информеры. Корректность отображения и функционала информера с модалкой из под группы`, async function () {
    const categoryGroup0Selector = `${mkTestId('category-group')}[data-id="deltaGroupId-bottomGroups-0"]`
    const informerSelector = `${categoryGroup0Selector} ${mkTestId('informer')}`

    const informerBackButton = `${mkTestId('informer-modal')} ${mkTestId('action-button')}[data-action-id="unset"]`
    const informerLinkButton = `${mkTestId('informer-modal')} ${mkTestId('action-button')}[data-action-id="link"]`

    await this.browser.openPage('/', deltaLayoutGridOptions)
    await this.browser.waitForElementExists(informerSelector)
    await this.browser.scrollToElement(informerSelector, {offsetY: -80})
    await this.browser.assertImage(mkTestId('main-page-layout'), {state: 'scrolled-to-group-informer'})
    await this.browser.waitForElementAndClick(informerSelector)
    await this.browser.assertImage(mkTestId('main-page-layout'), {state: 'informer-modal-viewed'})
    await this.browser.waitForElementAndClick(informerBackButton)
    await this.browser.assertImage(mkTestId('main-page-layout'), {state: 'informer-modal-closed-via-back-button'})
    await this.browser.waitForElementAndClick(informerSelector)
    await this.browser.waitForElementAndClick(informerLinkButton)
    await this.browser.waitForElementExists(mkTestId('category-page-layout'))
  })

  it('Информеры. Ничего не должно произойти на клик по информеру без модалки', async function () {
    const informerSelector = `${mkTestId('promo-informer')}${mkDataId(
      'lavka-frontend_informers__deltaPromoInformer-2',
    )}`
    await this.browser.openPage('/', deltaLayoutGridOptions)
    await this.browser.waitForElementAndClick(informerSelector)
    await this.browser.assertImage(mkTestId('main-page-layout'), {state: 'informer-clicked-and-nothing-happened'})
  })
  it('Разобранная категория. Общий вид и проверка, что такую категорию нельзя открыть', async function () {
    const categoryGroupSelector = `${mkTestId('category-group')}${mkDataId('deltaGroupSpecificId')}`
    const firstSoldOutCategoryCardSelector = `${categoryGroupSelector} [data-category-id="deltaCategorySoldOutId1"]`

    await this.browser.openPage('/', deltaLayoutGridOptions)
    await this.browser.waitForElementExists(categoryGroupSelector)
    await this.browser.scrollToElement(categoryGroupSelector, {offsetY: -80})
    await this.browser.assertImage(mkTestId('main-page-layout'), {state: 'general-view-of-sold-out-categories'})
    await this.browser.waitForElementAndClick(firstSoldOutCategoryCardSelector)
    await this.browser.assertImage(mkTestId('main-page-layout'), {
      state: 'clicked-on-sold-out-category-and-nothing-happened',
    })
  })
  it('Категория с товарами Товары 18+ и каруселью. Корректное отображение', async function () {
    const categoryGroupSelector = `${mkTestId('category-group')}${mkDataId(
      'deltaGroupCarouselWithRestrictionsAdult18Id',
    )}`

    await this.browser.openPage('/', deltaLayoutGridOptions)
    await this.browser.waitForElementExists(categoryGroupSelector)
    await this.browser.scrollToElement(categoryGroupSelector, {offsetY: -80})
    await this.browser.assertImage(mkTestId('main-page-layout'), {state: 'general-view-of-sold-out-categories'})
  })

  it('Категория с товарами Товары 18+ и каруселью. Проверка открытия и взаимодействия с модалкой подтверждения возраста', async function () {
    await this.browser.openPage('/', deltaLayoutGridOptions)
    await this.browser.waitForElementExists(categoryGroupAdult18Selector)
    await this.browser.scrollToElement(categoryGroupAdult18Selector, {offsetY: -80})
    await this.browser.waitForElementAndClick(firstProductInCarouselAdult18Selector)
    await this.browser.waitForElementExists(adultModal)
    await this.browser.assertImage(mkTestId('main-page-layout'), {
      state: 'adult-modal-opened',
    })
    await this.browser.waitForElementAndClick(`${adultModal} ${mkTestId('cancel-button')}`)
    await this.browser.assertImage(mkTestId('main-page-layout'), {
      state: 'adult-modal-cancelled',
    })
    await this.browser.waitForElementAndClick(firstProductInCarouselAdult18Selector)
    await this.browser.waitForElementAndClick(`${adultModal} ${mkTestId('confirm-button')}`)
    await this.browser.waitForElementExists(mkTestId('product-card-bottom-sheet'))
    await this.browser.assertImage(mkTestId('main-page-layout'), {
      state: 'adult-modal-confirmed',
    })
  })
  it(`Категория с товарами Товары 18+ и каруселью. После нажатия из карусели на кнопку 'Все', должна открыться категория с модалкой подтверждения возраста`, async function () {
    const allButtonOnCarousel = `${categoryGroupAdult18Selector} ${mkTestId('all-button')}`

    await this.browser.openPage('/', deltaLayoutGridOptions)
    await this.browser.waitForElementExists(categoryGroupAdult18Selector)
    await this.browser.scrollToElement(categoryGroupAdult18Selector, {offsetY: -80})
    await this.browser.waitForElementAndClick(allButtonOnCarousel)
    await this.browser.waitForElementExists(mkTestId('category-page-layout'))
    await this.browser.waitForElementExists(adultModal)
    await this.browser.assertImage(mkTestId('category-page-layout'))
  })
  it(`Категория с товарами Товары 18+ и каруселью. При клике по кнопке 'в корзину' на продукте карусели, после подтверждения возраста, товар должен добавиться в корзину`, async function () {
    const addToCartButton = `${firstProductInCarouselAdult18Selector} ${mkTestId('product-card-add-button')}`

    await this.browser.openPage('/', deltaLayoutGridOptions)
    await this.browser.waitForElementExists(categoryGroupAdult18Selector)
    await this.browser.scrollToElement(categoryGroupAdult18Selector, {offsetY: -80})
    await this.browser.waitForElementAndClick(addToCartButton)
    await this.browser.waitForElementExists(adultModal)
    await this.browser.waitForElementAndClick(`${adultModal} ${mkTestId('confirm-button')}`)
    await this.browser.waitForElementExists(mkTestId('cart-button'))
    await this.browser.assertImage(mkTestId('main-page-layout'))
  })
})
