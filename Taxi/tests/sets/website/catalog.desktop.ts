import { identifiers } from '@lavka/constants'

// TODO: сделать абсолютные импорты https://st.yandex-team.ru/LAVKAFRONT-4906
import { CatalogPageDesktop, CategoryPageDesktop, CatalogMenuItemCollapse } from '../../models'

describe('Каталог', function () {
  const deltaLayoutGridOptions = {
    cookies: {
      layoutId: identifiers.layoutDeltaId,
    },
  }

  it('yalavka-309: Открытие категорий из бокового меню навигации', async function () {
    const catalogPage = new CatalogPageDesktop(this)
    const firstCollapseItem = new CatalogMenuItemCollapse(this, { itemId: identifiers.groupDeltaA })
    const secondCollapseItem = new CatalogMenuItemCollapse(this, { itemId: identifiers.groupDeltaSpecific })

    await catalogPage.openPage(deltaLayoutGridOptions)
    await catalogPage.assertImage({ state: 'page-opened' })
    await firstCollapseItem.moveTo()
    await catalogPage.assertCatalogWrapperImage({ state: 'hovered-on-first-menu-item' })
    await firstCollapseItem.waitAndClick()
    await catalogPage.assertCatalogWrapperImage({ state: 'clicked-on-first-menu-item' })
    await secondCollapseItem.waitAndClick()
    await catalogPage.assertImage({ state: 'clicked-on-second-menu-item' })
  })
  it('yalavka-310, yalavka-311, yalavka-316: Отображение каталога при выборе категории и подкатегории', async function () {
    const catalogPage = new CatalogPageDesktop(this)
    const categoryPage = new CategoryPageDesktop(this)
    const firstCollapseItemCatalog = new CatalogMenuItemCollapse(this, { itemId: identifiers.groupDeltaA })
    const firstCollapseItemCategory = new CatalogMenuItemCollapse(this, { itemId: identifiers.categoryDeltaA })
    await catalogPage.openPage(deltaLayoutGridOptions)
    await firstCollapseItemCatalog.waitAndClick()
    await categoryPage.assertImage({ state: 'category-opened-from-left-nav-menu' })
    await firstCollapseItemCatalog.waitAndClickSubItem(identifiers.categoryDeltaA)
    await categoryPage.assertImage({ state: 'clicked-first-category' })
    await firstCollapseItemCategory.waitAndClickSubItem('subcategoryDelta-0-A')
    await categoryPage.assertImage({ state: 'clicked-first-subcategory' })
    await firstCollapseItemCategory.waitAndClickSubItem('subcategoryDelta-1-A')
    await categoryPage.assertImage({ state: 'clicked-second-subcategory' })
    await catalogPage.waitAndClickBreadCrumbs(1)
    await categoryPage.assertImage({ state: 'clicked-second-breadcrumb' })
    await catalogPage.waitAndClickBreadCrumbs(0)
    await categoryPage.assertImage({ state: 'clicked-first-breadcrumb' })
  })
})
