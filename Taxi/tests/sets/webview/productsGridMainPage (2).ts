import {identifiers} from '@lavka/constants'
import {CategoryGroupMobile} from '@lavka/tests/models'

import {CategoryPage, MainPage, ProductBottomSheet} from '../../models'

describe('Сетка товаров. Главная страница.', async function () {
  const deltaLayoutGridOptions = {
    cookies: {
      layoutId: 'deltaLayoutId',
    },
  }

  it('yalavka-221: Корректное отображение страницы без прокрутки', async function () {
    const mainPage = new MainPage(this)
    await mainPage.openPage(deltaLayoutGridOptions)
    await mainPage.assertImage()
  })
  it('yalavka-221: Корректное отображение, когда прокрутили к верхней группе', async function () {
    const mainPage = new MainPage(this)
    await mainPage.openPage(deltaLayoutGridOptions)
    await new CategoryGroupMobile(this, {groupId: identifiers.groupDeltaA}).scrollToSelf()
    await mainPage.assertImage()
  })
  it('yalavka-221: Корректное отображение, когда прокрутили к группе карусели', async function () {
    const mainPage = new MainPage(this)
    await mainPage.openPage(deltaLayoutGridOptions)
    await new CategoryGroupMobile(this, {groupId: identifiers.groupDeltaCarousel}).scrollToSelf()
    await mainPage.assertImage()
  })
  it('yalavka-221: Корректное отображение, когда прокрутили к группе после карусели', async function () {
    const mainPage = new MainPage(this)
    await mainPage.openPage(deltaLayoutGridOptions)
    await new CategoryGroupMobile(this, {groupId: identifiers.groupDeltaBottom1}).scrollToSelf()
    await mainPage.assertImage()
  })
  it('yalavka-221: Корректное отображение, когда прокрутили страницу вниз и вверх до упора', async function () {
    const mainPage = new MainPage(this)
    await mainPage.openPage(deltaLayoutGridOptions)
    await mainPage.scrollBodyToEdge({direction: 'down'})
    await mainPage.assertImage({state: 'scrolled-to-bottom'})
    await mainPage.scrollBodyToEdge({direction: 'up'})
    await mainPage.assertImage({state: 'scrolled-to-up'})
  })
  it('yalavka-221: Карусель категории. Корректная прокрутка и отображение аплифта вправо и обратно до упора', async function () {
    const mainPage = new MainPage(this)
    await mainPage.openPage(deltaLayoutGridOptions)
    const categoryGroup = await new CategoryGroupMobile(this, {groupId: identifiers.groupDeltaCarousel})
    await categoryGroup.scrollToSelf()
    await categoryGroup.scrollCarouselToEdge({direction: 'right'})
    await mainPage.assertImage({state: 'uplift-scrolled-to-right'})
    await categoryGroup.scrollCarouselToEdge({direction: 'left'})
    await mainPage.assertImage({state: 'uplift-scrolled-to-left'})
  })
  it(`yalavka-260: Карусель категории. При нажатии из аплифта на 'Все' открывается его категория`, async function () {
    const mainPage = new MainPage(this)
    const categoryPage = new CategoryPage(this)
    await mainPage.openPage(deltaLayoutGridOptions)
    await new CategoryGroupMobile(this, {groupId: identifiers.groupDeltaCarousel}).waitAndClickGroupAllButton()
    await categoryPage.waitForPageLoaded()
  })
  it(`yalavka-260: Карусель категории. При нажатии из аплифта на 'Смотреть все' открывается его категория`, async function () {
    const mainPage = new MainPage(this)
    const categoryPage = new CategoryPage(this)
    const categoryGroup = await new CategoryGroupMobile(this, {groupId: identifiers.groupDeltaCarousel})
    await mainPage.openPage(deltaLayoutGridOptions)
    await categoryGroup.scrollCarouselToEdge({direction: 'right'})
    await categoryGroup.clickMoreButton()
    await categoryPage.waitForPageLoaded()
  })
  it(`yalavka-259: Информеры. Корректность отображения и функционала информера с модалкой из service-info`, async function () {
    const mainPage = new MainPage(this)
    const categoryPage = new CategoryPage(this)
    await mainPage.openPage(deltaLayoutGridOptions)
    await mainPage.scrollToPromoInformer('lavka-frontend_informers__deltaPromoInformer-1')
    await mainPage.assertImage({state: 'informer-viewed'})
    await mainPage.waitAndClickOnPromoInformer('lavka-frontend_informers__deltaPromoInformer-1')
    await mainPage.assertImage({state: 'informer-modal-viewed'})
    // check correct for closing informer
    await mainPage.clickInformerModalActionUnsetButton()
    await mainPage.waitAndClickOnPromoInformer('lavka-frontend_informers__deltaPromoInformer-1')
    await mainPage.clickInformerModalActionLinkButton()
    await categoryPage.waitForPageLoaded()
  })
  it(`yalavka-259: Информеры. Корректность отображения и функционала информера с модалкой из под группы`, async function () {
    const mainPage = new MainPage(this)
    const categoryPage = new CategoryPage(this)
    const categoryGroup = await new CategoryGroupMobile(this, {groupId: identifiers.groupDeltaBottom1})
    await mainPage.openPage(deltaLayoutGridOptions)
    await categoryGroup.scrollToInformer()
    await mainPage.assertImage({state: 'scrolled-to-group-informer'})
    await categoryGroup.waitAndClickOnInformer()
    await mainPage.assertImage({state: 'informer-modal-viewed'})
    // check correct for closing informer
    await mainPage.clickInformerModalActionUnsetButton()
    await categoryGroup.waitAndClickOnInformer()
    await mainPage.clickInformerModalActionLinkButton()
    await categoryPage.waitForPageLoaded()
  })

  it('yalavka-259: Информеры. Ничего не должно произойти на клик по информеру без модалки', async function () {
    const mainPage = new MainPage(this)
    await mainPage.openPage(deltaLayoutGridOptions)
    await mainPage.waitAndClickOnPromoInformer('lavka-frontend_informers__deltaPromoInformer-2')
    await mainPage.assertImage({state: 'informer-clicked-and-nothing-happened'})
  })
  it('yalavka-264: Разобранная категория. Общий вид и проверка, что такую категорию нельзя открыть', async function () {
    const mainPage = new MainPage(this)
    await mainPage.openPage(deltaLayoutGridOptions)
    const categoryGroup = await new CategoryGroupMobile(this, {groupId: identifiers.groupDeltaSpecific})
    await categoryGroup.scrollToSelf()
    await mainPage.assertImage({state: 'general-view-of-sold-out-categories'})
    await categoryGroup.waitAndClickCategoryCard(identifiers.categoryDeltaSoldOut1)
    await mainPage.assertImage({state: 'clicked-on-sold-out-category-and-nothing-happened'})
  })
  it('yalavka-265: Категория с товарами Товары 18+ и каруселью. Корректное отображение', async function () {
    const mainPage = new MainPage(this)
    await mainPage.openPage(deltaLayoutGridOptions)
    await new CategoryGroupMobile(this, {groupId: identifiers.groupDeltaCarouselWithRestrictionsAdult18}).scrollToSelf()
    await mainPage.assertImage()
  })

  it('yalavka-265: Категория с товарами Товары 18+ и каруселью. Проверка открытия и взаимодействия с модалкой подтверждения возраста', async function () {
    const mainPage = new MainPage(this)
    const productCard = new ProductBottomSheet(this)
    const categoryGroup = new CategoryGroupMobile(this, {
      groupId: identifiers.groupDeltaCarouselWithRestrictionsAdult18,
    })

    await mainPage.openPage(deltaLayoutGridOptions)
    await categoryGroup.scrollToSelf()
    await categoryGroup.waitAndClickProduct('product-id-deltaProductWithRestrictionsAdult18Id-0')
    await mainPage.waitForModal('adult-modal')
    await mainPage.assertImage({state: 'adult-modal-opened'})
    await mainPage.waitAndClickForModalCancelButton('adult-modal')
    await mainPage.assertImage({state: 'adult-modal-cancelled'})
    await categoryGroup.waitAndClickProduct('product-id-deltaProductWithRestrictionsAdult18Id-0')
    await mainPage.waitAndClickForModalConfirmButton('adult-modal')
    await productCard.waitForExists()
    await mainPage.assertImage({state: 'adult-modal-confirmed'})
  })
  it(`yalavka-265: Категория с товарами Товары 18+ и каруселью. После нажатия из карусели на кнопку 'Все', должна открыться категория с модалкой подтверждения возраста`, async function () {
    const mainPage = new MainPage(this)
    const categoryPage = new CategoryPage(this)
    const categoryGroup = new CategoryGroupMobile(this, {
      groupId: identifiers.groupDeltaCarouselWithRestrictionsAdult18,
    })
    await mainPage.openPage(deltaLayoutGridOptions)
    await categoryGroup.scrollToSelf()
    await categoryGroup.waitAndClickGroupAllButton()
    await categoryPage.waitForPageLoaded()
    await categoryPage.waitForModal('adult-modal')
    await categoryPage.assertImage()
  })
  it(`yalavka-265: Категория с товарами Товары 18+ и каруселью. При клике по кнопке 'в корзину' на продукте карусели, после подтверждения возраста, товар должен добавиться в корзину`, async function () {
    const mainPage = new MainPage(this)
    const categoryGroup = new CategoryGroupMobile(this, {
      groupId: identifiers.groupDeltaCarouselWithRestrictionsAdult18,
    })
    await mainPage.openPage(deltaLayoutGridOptions)
    await categoryGroup.scrollToSelf()
    await categoryGroup.addProduct('product-id-deltaProductWithRestrictionsAdult18Id-0')
    await mainPage.waitForModal('adult-modal')
    await mainPage.waitAndClickForModalConfirmButton('adult-modal')
    await mainPage.waitForCartButtonActive()
    await mainPage.assertImage()
  })
})
