// Сетка товаров. Страница категории, карусель подкатегории

import {
  deltaCategoryBubblesId,
  deltaCategoryHeroId,
  deltaCategoryThreeInRowId,
  deltaCategoryTwoInRowId,
} from '../../constants/common'
import {mkTestId} from '../../utils/mkTestId'

describe('Сетка товаров. Страница категории.', async function () {
  const deltaCategoryTwoInRowUrl = `/?group=0f1846f41ac8453680a175023a77fae3&category=${deltaCategoryTwoInRowId}`
  const deltaCategoryThreeInRowUrl = `/?group=0f1846f41ac8453680a175023a77fae3&category=${deltaCategoryThreeInRowId}`
  const deltaCategoryBubblesUrl = `/?group=0f1846f41ac8453680a175023a77fae3&category=${deltaCategoryBubblesId}`
  const deltaCategoryHeroUrl = `/?group=0f1846f41ac8453680a175023a77fae3&category=${deltaCategoryHeroId}`

  const bubblePlateWithCompletedAnimation = `${mkTestId(
    'navigation-carousel bubble-plate',
  )}[data-animation-state="completed"]`

  it(`Страница категории, карточки 'два в ряд', корректный вид при открытии, прокрутке`, async function () {
    await this.browser.openPage(deltaCategoryTwoInRowUrl)
    await this.browser.waitForElementExists(mkTestId('category-page-layout'))
    await this.browser.assertImage(mkTestId('category-page-layout'), {state: 'page-opened'})
    await this.browser.scrollByElement('body', {y: 250})
    await this.browser.assertImage(mkTestId('category-page-layout'), {state: 'page-a-little-scrolled'})
    await this.browser.scrollToElementEdge('body', {direction: 'down'})
    await this.browser.assertImage(mkTestId('category-page-layout'), {state: 'page-scrolled-to-bottom'})
  })
  it(`Страница категории, карточки 'три в ряд', корректный вид при открытии, прокрутке`, async function () {
    await this.browser.openPage(deltaCategoryThreeInRowUrl)
    await this.browser.waitForElementExists(mkTestId('category-page-layout'))
    await this.browser.assertImage(mkTestId('category-page-layout'), {state: 'page-opened'})
    await this.browser.scrollByElement('body', {y: 250})
    await this.browser.assertImage(mkTestId('category-page-layout'), {state: 'page-a-little-scrolled'})
    await this.browser.scrollToElementEdge('body', {direction: 'down'})
    await this.browser.assertImage(mkTestId('category-page-layout'), {state: 'page-scrolled-to-bottom'})
  })
  it(`Страница категории, баблы подкатегорий, корректное отображение без прокрутки страницы`, async function () {
    await this.browser.openPage(deltaCategoryBubblesUrl)
    await this.browser.waitForElementExists(mkTestId('navigation-bubbles'))
    await this.browser.assertImage(mkTestId('category-page-layout'), {state: 'page-opened'})
    await this.browser.waitForElementAndClick(mkTestId('navigation-bubbles more-button'))
    await this.browser.assertImage(mkTestId('category-page-layout'), {state: 'bubbles-more-button-clicked'})
  })
  it(`Страница категории, баблы подкатегорий, корректное отображение при прокрутке при кликах по баблам навигации не из карусели`, async function () {
    await this.browser.openPage(deltaCategoryBubblesUrl)
    await this.browser.waitForElementExists(mkTestId('navigation-bubbles'))
    await this.browser.scrollByElement('body', {y: 250})
    await this.browser.waitForElementExists(bubblePlateWithCompletedAnimation)
    await this.browser.assertImage(mkTestId('category-page-layout'), {state: 'page-a-little-scrolled-down'})
    await this.browser.scrollByElement('body', {y: 600})
    await this.browser.waitForElementExists(bubblePlateWithCompletedAnimation)
    await this.browser.assertImage(mkTestId('category-page-layout'), {state: 'page-scrolled-more-to-down'})
    await this.browser.scrollToElementEdge('body', {direction: 'down'})
    await this.browser.waitForElementExists(bubblePlateWithCompletedAnimation)
    await this.browser.assertImage(mkTestId('category-page-layout'), {state: 'page-scrolled-to-bottom'})
    await this.browser.scrollToElementEdge('body', {direction: 'up'})
    await this.browser.assertImage(mkTestId('category-page-layout'), {state: 'page-return-scroll-to-top'})
  })
  it(`Страница категории, баблы подкатегорий, корректное отображение при прокрутке при кликах по баблам навигации из карусели`, async function () {
    await this.browser.openPage(deltaCategoryBubblesUrl)
    await this.browser.waitForElementAndClick(mkTestId('navigation-bubbles more-button'))
    await this.browser.scrollByElement('body', {y: 250})
    await this.browser.assertImage(mkTestId('category-page-layout'), {state: 'page-a-little-scrolled-down'})
    await this.browser.scrollByElement('body', {y: 600})
    await this.browser.waitForElementExists(bubblePlateWithCompletedAnimation)
    await this.browser.assertImage(mkTestId('category-page-layout'), {state: 'page-scrolled-more-to-down'})
    await this.browser.scrollToElementEdge('body', {direction: 'down'})
    await this.browser.waitForElementExists(bubblePlateWithCompletedAnimation)
    await this.browser.assertImage(mkTestId('category-page-layout'), {state: 'page-scrolled-to-bottom'})
    await this.browser.scrollToElementEdge('body', {direction: 'up'})
    await this.browser.assertImage(mkTestId('category-page-layout'), {state: 'page-return-scroll-to-top'})
  })
  it(`Страница категории, баблы подкатегорий. Корректный скролл страницы при кликах по баблам навигации (не из карусели)`, async function () {
    const firstBubble = `${mkTestId('navigation-bubbles')} [data-bubble-id="deltaSubcategoryBubblesId-0"]`
    const someInitiallyHiddenBubble = `${mkTestId(
      'navigation-bubbles',
    )} [data-bubble-id="deltaSubcategoryBubblesId-15"]`
    const lastBubble = `${mkTestId('navigation-bubbles')} [data-bubble-id="deltaSubcategoryBubblesId-19"]`

    await this.browser.openPage(deltaCategoryBubblesUrl)
    await this.browser.waitForElementAndClick(firstBubble)
    await this.browser.waitForElementScrollReleased('body')
    await this.browser.assertImage(mkTestId('category-page-layout'), {state: 'clicked-on-first-bubble'})
    await this.browser.scrollToElementEdge('body', {direction: 'up'})
    // т.к. someInitiallyHiddenBubble скрыт, должны развернуть bubbles
    await this.browser.waitForElementAndClick(mkTestId('navigation-bubbles more-button'))
    await this.browser.waitForElementAndClick(someInitiallyHiddenBubble)
    await this.browser.waitForElementScrollReleased('body')
    await this.browser.waitForElementExists(bubblePlateWithCompletedAnimation)
    await this.browser.assertImage(mkTestId('category-page-layout'), {state: 'clicked-on-some-initially-hidden-bubble'})
    await this.browser.scrollToElementEdge('body', {direction: 'up'})
    await this.browser.waitForElementAndClick(lastBubble)
    await this.browser.waitForElementScrollReleased('body')
    await this.browser.assertImage(mkTestId('category-page-layout'), {state: 'clicked-on-last-bubble'})
  })
  it(`Страница категории, баблы подкатегорий. Корректный скролл страницы при кликах по баблам, которые не крайние в навигации из карусели`, async function () {
    const secondNavigationBubble = `${mkTestId('navigation-bubbles')} [data-bubble-id="deltaSubcategoryBubblesId-1"]`
    const someInitiallyHiddenBubble = `${mkTestId(
      'navigation-carousel',
    )} [data-bubble-id="deltaSubcategoryBubblesId-15"]`

    await this.browser.openPage(deltaCategoryBubblesUrl)
    await this.browser.waitForElementAndClick(secondNavigationBubble)
    await this.browser.waitForElementScrollReleased('body')
    await this.browser.waitForElementExists(bubblePlateWithCompletedAnimation)
    await this.browser.assertImage(mkTestId('category-page-layout'), {
      state: 'second-bubble-clicked-and-carousel-showed',
    })
    await this.browser.scrollToElement(someInitiallyHiddenBubble)
    await this.browser.waitForElementExists(bubblePlateWithCompletedAnimation)
    await this.browser.assertImage(mkTestId('category-page-layout'), {
      state: 'scrolled-into-some-initially-hidden-bubble',
    })
    await this.browser.waitForElementAndClick(someInitiallyHiddenBubble)
    await this.browser.waitForElementScrollReleased('body')
    await this.browser.waitForElementExists(bubblePlateWithCompletedAnimation)
    await this.browser.assertImage(mkTestId('category-page-layout'), {
      state: 'clicked-on-bubble-to-which-scroll-has-moved',
    })
  })

  it(`Страница категории, баблы подкатегорий. Корректный скролл страницы при кликах по баблам, которые крайние в навигации из карусели`, async function () {
    const secondNavigationBubble = `${mkTestId('navigation-bubbles')} [data-bubble-id="deltaSubcategoryBubblesId-1"]`
    const carouselScrollContainer = mkTestId('navigation-carousel horizontal-scrollable-container')
    const lastCarouselBubble = `${mkTestId('navigation-carousel')} [data-bubble-id="deltaSubcategoryBubblesId-19"]`
    const firstCarouselBubble = `${mkTestId('navigation-carousel')} [data-bubble-id="deltaSubcategoryBubblesId-0"]`

    await this.browser.openPage(deltaCategoryBubblesUrl)
    // чтобы появилась карусель, кликаем на второй бабл
    await this.browser.waitForElementAndClick(secondNavigationBubble)
    await this.browser.waitForElementScrollReleased('body')
    await this.browser.scrollToElementEdge(carouselScrollContainer, {direction: 'right'})
    await this.browser.assertImage(mkTestId('category-page-layout'), {
      state: 'carousel-scrolled-right',
    })
    await this.browser.waitForElementAndClick(lastCarouselBubble)
    await this.browser.waitForElementScrollReleased('body')
    await this.browser.waitForElementExists(bubblePlateWithCompletedAnimation)
    await this.browser.assertImage(mkTestId('category-page-layout'), {
      state: 'clicked-on-last-carousel-bubble',
    })
    await this.browser.scrollToElementEdge(carouselScrollContainer, {direction: 'left'})
    await this.browser.assertImage(mkTestId('category-page-layout'), {
      state: 'scrolled-carousel-to-start',
    })
    await this.browser.waitForElementAndClick(firstCarouselBubble)
    await this.browser.waitForElementScrollReleased('body')
    await this.browser.assertImage(mkTestId('category-page-layout'), {
      state: 'clicked-on-first-carousel-bubble-and-carousel-hide',
    })
  })
  it(`Страница категории, Hero banner. Корректность отображения.`, async function () {
    await this.browser.openPage(deltaCategoryHeroUrl)
    await this.browser.waitForElementExists(mkTestId('category-page-layout'))
    await this.browser.assertImage(mkTestId('category-page-layout'), {state: 'page-opened'})
  })
  it(`Страница категории, Hero banner. Скролл к подкатегории при нажатии на первый бабл`, async function () {
    const firstBubble = `${mkTestId('navigation-bubbles')} [data-bubble-id="deltaSubcategoryHeroId-0"]`
    await this.browser.openPage(deltaCategoryHeroUrl)
    await this.browser.waitForElementAndClick(firstBubble)
    await this.browser.waitForElementScrollReleased('body')
    await this.browser.assertImage(mkTestId('category-page-layout'), {state: 'clicked-on-first-bubble'})
  })
  it(`Страница категории, Hero banner. Скролл к подкатегории и открытие карусели навигации при нажатии на второй бабл`, async function () {
    const secondBubble = `${mkTestId('navigation-bubbles')} [data-bubble-id="deltaSubcategoryHeroId-1"]`
    await this.browser.openPage(deltaCategoryHeroUrl)
    await this.browser.waitForElementAndClick(secondBubble)
    await this.browser.waitForElementScrollReleased('body')
    await this.browser.assertImage(mkTestId('category-page-layout'), {state: 'clicked-on-first-bubble'})
  })
})
