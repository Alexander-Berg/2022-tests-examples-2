import {identifiers} from '@lavka/constants'

import {CategoryPage} from '../../models'

describe('Сетка товаров. Страница категории.', async function () {
  const firstBubbleId = 'deltaSubcategoryBubblesId-0'
  const secondBubbleId = 'deltaSubcategoryBubblesId-1'
  const someNotExtremeBubbleId = 'deltaSubcategoryBubblesId-15'
  const lastBubbleId = 'deltaSubcategoryBubblesId-19'

  it(`yalavka-263: Страница категории, карточки 'два в ряд', корректный вид при открытии, прокрутке`, async function () {
    const categoryPage = new CategoryPage(this)
    await categoryPage.openCategoryPage({categoryId: identifiers.categoryDeltaTwoInRow})
    await categoryPage.assertImage({state: 'page-opened'})
    await categoryPage.scrollBodyTo(250)
    await categoryPage.assertImage({state: 'page-a-little-scrolled'})
    await categoryPage.scrollBodyToEdge({direction: 'down'})
    await categoryPage.assertImage({state: 'page-scrolled-to-bottom'})
  })
  it(`yalavka-262: Страница категории, карточки 'три в ряд', корректный вид при открытии, прокрутке`, async function () {
    const categoryPage = new CategoryPage(this)
    await categoryPage.openCategoryPage({categoryId: identifiers.categoryDeltaThreeInRow})
    await categoryPage.assertImage({state: 'page-opened'})
    await categoryPage.scrollBodyTo(250)
    await categoryPage.assertImage({state: 'page-a-little-scrolled'})
    await categoryPage.scrollBodyToEdge({direction: 'down'})
    await categoryPage.assertImage({state: 'page-scrolled-to-bottom'})
  })
  it(`yalavka-267: Страница категории, баблы подкатегорий, корректное отображение без прокрутки страницы`, async function () {
    const categoryPage = new CategoryPage(this)
    await categoryPage.openCategoryPage({categoryId: identifiers.categoryDeltaBubbles})
    await categoryPage.waitForNavigationBubbles()
    await categoryPage.assertImage({state: 'page-opened'})
    await categoryPage.waitAndClickOnNavigationBubbleMoreButton()
    await categoryPage.assertImage({state: 'bubbles-more-button-clicked'})
  })
  it(`yalavka-267: Страница категории, баблы подкатегорий, корректное отображение при прокрутке при кликах по баблам навигации не из карусели`, async function () {
    const categoryPage = new CategoryPage(this)
    await categoryPage.openCategoryPage({categoryId: identifiers.categoryDeltaBubbles})
    await categoryPage.waitForNavigationBubbles()
    await categoryPage.scrollBodyTo(250)
    await categoryPage.waitForBubblePlateAnimationCompleted()
    await categoryPage.assertImage({state: 'page-a-little-scrolled-down'})
    await categoryPage.scrollBodyTo(600)
    await categoryPage.waitForBubblePlateAnimationCompleted()
    await categoryPage.assertImage({state: 'page-scrolled-more-to-down'})
    await categoryPage.scrollBodyToEdge({direction: 'down'})
    await categoryPage.waitForBubblePlateAnimationCompleted()
    await categoryPage.assertImage({state: 'page-scrolled-to-bottom'})
    await categoryPage.scrollBodyToEdge({direction: 'up'})
    await categoryPage.assertImage({state: 'page-return-scroll-to-top'})
  })
  it(`yalavka-267: Страница категории, баблы подкатегорий, корректное отображение при прокрутке при кликах по баблам навигации из карусели`, async function () {
    const categoryPage = new CategoryPage(this)
    await categoryPage.openCategoryPage({categoryId: identifiers.categoryDeltaBubbles})
    await categoryPage.waitAndClickOnNavigationBubbleMoreButton()
    await categoryPage.scrollBodyTo(250)
    await categoryPage.assertImage({state: 'page-a-little-scrolled-down'})
    await categoryPage.scrollBodyTo(600)
    await categoryPage.waitForBubblePlateAnimationCompleted()
    await categoryPage.assertImage({state: 'page-scrolled-more-to-down'})
    await categoryPage.scrollBodyToEdge({direction: 'down'})
    await categoryPage.waitForBubblePlateAnimationCompleted()
    await categoryPage.assertImage({state: 'page-scrolled-to-bottom'})
    await categoryPage.scrollBodyToEdge({direction: 'up'})
    await categoryPage.assertImage({state: 'page-return-scroll-to-top'})
  })
  it(`yalavka-267: Страница категории, баблы подкатегорий. Корректный скролл страницы при кликах по баблам навигации (не из карусели)`, async function () {
    const categoryPage = new CategoryPage(this)
    await categoryPage.openCategoryPage({categoryId: identifiers.categoryDeltaBubbles})
    await categoryPage.waitAndClickOnNavigationBubble(firstBubbleId, {skipWaitingAnimations: true})
    await categoryPage.assertImage({state: 'clicked-on-first-bubble'})
    await categoryPage.scrollBodyToEdge({direction: 'up'})
    await categoryPage.waitAndClickOnNavigationBubbleMoreButton()
    // scroll to some bubble that is outside of screen
    await categoryPage.waitAndClickOnNavigationBubble(someNotExtremeBubbleId)
    await categoryPage.assertImage({state: 'clicked-on-some-initially-hidden-bubble'})
    await categoryPage.waitAndClickOnNavigationBubble(lastBubbleId)
    await categoryPage.assertImage({state: 'clicked-on-last-bubble'})
  })
  it(`yalavka-267: Страница категории, баблы подкатегорий. Корректный скролл страницы при кликах по баблам, которые не крайние в навигации из карусели`, async function () {
    const categoryPage = new CategoryPage(this)
    await categoryPage.openCategoryPage({categoryId: identifiers.categoryDeltaBubbles})
    await categoryPage.waitAndClickOnNavigationBubble(secondBubbleId, {
      skipWaitingAnimations: true,
    })
    await categoryPage.assertImage({state: 'second-bubble-clicked-and-carousel-showed'})
    await categoryPage.scrollToBubbleInBubbleNavigationContainer(someNotExtremeBubbleId)
    await categoryPage.assertImage({state: 'scrolled-into-some-initially-hidden-bubble'})
    await categoryPage.waitAndClickOnNavigationCarouselBubble(someNotExtremeBubbleId)
    await categoryPage.assertImage({state: 'clicked-on-bubble-to-which-scroll-has-moved'})
  })

  it(`yalavka-267: Страница категории, баблы подкатегорий. Корректный скролл страницы при кликах по баблам, которые крайние в навигации из карусели`, async function () {
    const categoryPage = new CategoryPage(this)
    await categoryPage.openCategoryPage({categoryId: identifiers.categoryDeltaBubbles})
    // to view carousel click on second bubble
    await categoryPage.waitAndClickOnNavigationBubble(secondBubbleId)
    await categoryPage.scrollNavigationCarouselToEdge({direction: 'right'})
    await categoryPage.assertImage({state: 'carousel-scrolled-right'})
    await categoryPage.waitAndClickOnNavigationCarouselBubble(lastBubbleId)
    await categoryPage.assertImage({state: 'clicked-on-last-carousel-bubble'})
    await categoryPage.waitAndClickOnNavigationCarouselBubble(firstBubbleId, {
      skipWaitingAnimations: true,
    })
    await categoryPage.assertImage({state: 'clicked-on-first-carousel-bubble-and-carousel-hide'})
  })
  it(`yalavka-268: Страница категории, Hero banner. Корректность отображения`, async function () {
    const categoryPage = new CategoryPage(this)
    await categoryPage.openCategoryPage({categoryId: identifiers.categoryWithHero})
    await categoryPage.assertImage({state: 'page-opened'})
  })
  it(`yalavka-268: Страница категории, Hero banner. Скролл к подкатегории при нажатии на первый бабл`, async function () {
    const categoryPage = new CategoryPage(this)
    await categoryPage.openCategoryPage({categoryId: identifiers.categoryWithHero})
    await categoryPage.waitAndClickOnNavigationBubble('deltaSubcategoryHeroId-0', {skipWaitingAnimations: true})
    await categoryPage.assertImage({state: 'clicked-on-first-bubble'})
  })
  it(`yalavka-268: Страница категории, Hero banner. Скролл к подкатегории и открытие карусели навигации при нажатии на второй бабл`, async function () {
    const categoryPage = new CategoryPage(this)
    await categoryPage.openCategoryPage({categoryId: identifiers.categoryWithHero})
    await categoryPage.waitAndClickOnNavigationBubble('deltaSubcategoryHeroId-1')
    await categoryPage.assertImage({state: 'clicked-on-first-bubble'})
  })
})
