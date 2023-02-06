import {identifiers} from '@lavka/constants'
import {makeExperimentsConfigCookies, makeExperimentsCookies, mkTestId} from '@lavka/tests'
import {PRODUCT_BLOCKS_CONFIG_DEFAULT} from '@lavka/tests/fixtures/experiments/configs.webview'

import {CategoryPage} from '../../models'
import {getMockServerApiUrl} from '../../utils'

const comboTestsCookies = {
  ...makeExperimentsCookies({
    'lavka-frontend_sku_add_on_bottom': {enabled: true},
  }),
}

describe('Мультиплатформа: Карточка товара', async function () {
  it('yalavka-145: Открытие простой карточки товара', async function () {
    const category = new CategoryPage(this)
    await category.openCategoryPage()
    const bottomSheet = await category.openProduct(identifiers.productBase)
    await bottomSheet.assertImage()
  })

  it('Открытие простой карточки товара с тостом', async function () {
    const category = new CategoryPage(this)
    await category.openCategoryPage(undefined, {
      cookies: {
        ...makeExperimentsConfigCookies({
          'lavka-frontend_product_blocks': {
            ...PRODUCT_BLOCKS_CONFIG_DEFAULT,
            scrollToDescriptionButtonDisplayCount: 10,
          },
        }),
      },
    })
    const bottomSheet = await category.openProduct(identifiers.productBase)
    await bottomSheet.assertItemDetailsToast()
    await bottomSheet.assertImage({state: 'product-card-with-toast-opened'})
    await bottomSheet.clickItemDetailsToast()
    await bottomSheet.waitForBodyScrollReleased()
    await bottomSheet.assertImage({state: 'clicked-on-toast'})
  })

  it('yalavka-146: Добавление товара в корзину', async function () {
    const category = new CategoryPage(this)
    await category.openCategoryPage()
    const bottomSheet = await category.openProduct(identifiers.productBase)
    await bottomSheet.clickAddToCart()
    await bottomSheet.assertCartButtonPriceText(55)
    await bottomSheet.assertImage()
  })
  it('yalavka-147: Изменение количества товара в корзине', async function () {
    const category = new CategoryPage(this)
    await category.openCategoryPage()
    const bottomSheet = await category.openProduct(identifiers.productBase)
    await bottomSheet.clickAddToCart()
    await bottomSheet.assertCartButton()
    await bottomSheet.clickAddSpin()
    await bottomSheet.assertCartButtonPriceText(55 * 2)
    await bottomSheet.assertImage()
  })
  it('yalavka-149: Удаление товара из корзины', async function () {
    const category = new CategoryPage(this)
    await category.openCategoryPage()
    const bottomSheet = await category.openProduct(identifiers.productBase)
    await bottomSheet.clickAddToCart()
    await bottomSheet.assertCartButton()
    await bottomSheet.clickRemoveSpin()
    await bottomSheet.assertCartButton({reverse: true})
    await bottomSheet.assertImage()
  })
  it('yalavka-238: Отображение карточки товара с бонусами Плюс', async function () {
    const category = new CategoryPage(this)
    await category.openCategoryPage({categoryId: identifiers.categorySigma})
    const bottomSheet = await category.openProduct(identifiers.productSigmaWithCashback)
    await bottomSheet.assertImage()
  })
  it('yalavka-239: Отображение стикеров', async function () {
    const category = new CategoryPage(this)
    await category.openCategoryPage({categoryId: identifiers.categorySigma})
    const bottomSheet = await category.openProduct(identifiers.productSigmaWithStickers)
    await bottomSheet.assertImage()
  })
  it('Отображение информеров', async function () {
    const category = new CategoryPage(this)
    await category.openCategoryPage({categoryId: identifiers.categorySigma})
    const bottomSheet = await category.openProduct(identifiers.productSigmaWithInformers)
    await bottomSheet.assertImage()
  })
  it('Отображение продукта без картинки', async function () {
    const category = new CategoryPage(this)
    await category.openCategoryPage({categoryId: identifiers.categorySigma})
    const bottomSheet = await category.openProduct(identifiers.productSigmaNoImage)
    await bottomSheet.assertImage()
  })
  it('Отображение товара с истекающим сроком годности', async function () {
    const category = new CategoryPage(this)
    await category.openCategoryPage({categoryId: identifiers.categorySigma})
    const bottomSheet = await category.openProduct(identifiers.productSigmaExpiring)
    await bottomSheet.assertImage()
  })
  it('Отображение весового товара', async function () {
    const category = new CategoryPage(this)
    await category.openCategoryPage({categoryId: identifiers.categorySigma})
    const bottomSheet = await category.openProduct(identifiers.productSigmaWithGrades)
    await bottomSheet.assertImage()
  })
  it('yalavka-247: Отображение товара со скидкой', async function () {
    const category = new CategoryPage(this)
    await category.openCategoryPage({categoryId: identifiers.categorySigma})
    const bottomSheet = await category.openProduct(identifiers.productSigmaWithDiscount)
    await bottomSheet.assertImage()
  })
  it('yalavka-257: Открытие карточки с апсейлом', async function () {
    const category = new CategoryPage(this)
    await category.openCategoryPage({categoryId: identifiers.categorySigma})
    const bottomSheet = await category.openProduct(identifiers.productSigmaWithUpsale)
    await bottomSheet.assertImage()
  })
  it('yalavka-257: Отображение с доскроллированием до апсейла', async function () {
    const category = new CategoryPage(this)
    await category.openCategoryPage({categoryId: identifiers.categorySigma})
    const bottomSheet = await category.openProduct(identifiers.productSigmaWithUpsale)
    const upsale = bottomSheet.getUpsale()
    await upsale.scrollToUpsale({scrollableContainerSelector: mkTestId('bottom-sheet-body')})
    await bottomSheet.assertImage({state: 'scrolled-to-upsale'})
    await upsale.scrollToRightEdge()
    await bottomSheet.assertImage({state: 'upsale-scrolled-right'})
  })
  it('yalavka-254: Добавление товара в корзину из апсейла', async function () {
    const category = new CategoryPage(this)
    await category.openCategoryPage({categoryId: identifiers.categorySigma})
    const bottomSheet = await category.openProduct(identifiers.productSigmaWithUpsale)
    const upsale = bottomSheet.getUpsale()
    await upsale.scrollToUpsale({scrollableContainerSelector: mkTestId('bottom-sheet-body')})
    await upsale.clickAddProductToCart('product-id-upsaleAlphaProduct')
    await bottomSheet.assertCartButton()
    await bottomSheet.assertImage()
  })
  it('yalavka-255,yalavka-256: Редактирование количества добавленного в корзину товара из апсейла', async function () {
    const category = new CategoryPage(this)
    await category.openCategoryPage({categoryId: identifiers.categorySigma})
    const bottomSheet = await category.openProduct(identifiers.productSigmaWithUpsale)
    const upsale = bottomSheet.getUpsale()
    await upsale.scrollToUpsale({scrollableContainerSelector: mkTestId('bottom-sheet-body')})
    await upsale.clickAddProductToCart('product-id-upsaleAlphaProduct')
    await upsale.clickAddProductSpin('product-id-upsaleAlphaProduct')
    await bottomSheet.assertCartButtonPriceText(55 * 2)
    await bottomSheet.assertCartButton()
    await bottomSheet.assertImage({state: 'item-added-to-cart-twice'})
    await upsale.clickRemoveProductSpin('product-id-upsaleAlphaProduct')
    await bottomSheet.assertCartButtonPriceText(55)
    await bottomSheet.assertImage({state: 'one-item-removed'})
  })

  it('yalavka-517: Открытие категории с комбо товарами, проверка вида сниппетов', async function () {
    const category = new CategoryPage(this)
    await category.openCategoryPage(
      {
        categoryId: identifiers.categoryWithBundles,
      },
      {
        cookies: comboTestsCookies,
      },
    )
    await category.waitAndClickOnNavigationBubble('subcategoryWithBundles', {
      skipWaitingAnimations: true,
    })
    await category.assertImage({state: 'subcategory-with-bundles'})
    await category.waitAndClickOnNavigationBubble('subcategoryWithBundleProducts', {
      skipWaitingAnimations: true,
    })
    await category.assertImage({state: 'subcategory-with-bundle-products'})
  })

  it('yalavka-518: Открытие карточки мета-товара комбо с выбором, доскролливание до опций', async function () {
    const category = new CategoryPage(this)
    await category.openCategoryPage(
      {
        categoryId: identifiers.categoryWithBundles,
      },
      {
        cookies: comboTestsCookies,
      },
    )
    const bottomSheet = await category.openProduct(identifiers.productMetaWithBundles)
    await bottomSheet.assertImage({state: 'default-opened'})
    await bottomSheet.scrollToBundleOptions()
    await bottomSheet.assertImage({state: 'bundle-options'})
    await bottomSheet.scrollToBundleParts()
    await bottomSheet.assertImage({state: 'bundle-parts'})
  })

  it('yalavka-519: Открытие карточки мета-товара комбо без выбора', async function () {
    const category = new CategoryPage(this)
    await category.openCategoryPage(
      {
        categoryId: identifiers.categoryWithBundles,
      },
      {
        cookies: comboTestsCookies,
      },
    )
    const bottomSheet = await category.openProduct(identifiers.productMetaWithBundlesStatic)
    await bottomSheet.assertImage()
  })

  it('yalavka-520: Открытие карточки товара, входящего в комбо без выбора', async function () {
    const category = new CategoryPage(this)
    await category.openCategoryPage(
      {
        categoryId: identifiers.categoryWithBundles,
      },
      {
        cookies: comboTestsCookies,
      },
    )
    const bottomSheet = await category.openProduct(identifiers.productWithRelatedSingleSelectionCombo)
    await bottomSheet.assertImage({state: 'product-sheet-opened'})

    await bottomSheet.clickOnAvailableBundleItem(0)
    await bottomSheet.assertImage({state: 'bundle-sheet-default'})
  })

  it('yalavka-521: Открытие карточки товара, входящего в комбо c выбором', async function () {
    const category = new CategoryPage(this)
    await category.openCategoryPage(
      {
        categoryId: identifiers.categoryWithBundles,
      },
      {
        cookies: comboTestsCookies,
      },
    )
    const bottomSheet = await category.openProduct(identifiers.productWithRelatedSingleSelectionGroupCombo)
    await bottomSheet.assertImage({state: 'product-sheet-opened'})

    const bundleBottomSheet = await bottomSheet.clickOnAvailableBundleItem(0)
    await bundleBottomSheet.clickReplaceButton(0)
    await bottomSheet.assertImage({state: 'bundle-replace-sheet-default'})
  })

  it('yalavka-522: Открытие карточки товара, входящего в комбо c неуникальным выбором ("Шоколадки")', async function () {
    const category = new CategoryPage(this)
    await category.openCategoryPage(
      {
        categoryId: identifiers.categoryWithBundles,
      },
      {
        cookies: comboTestsCookies,
      },
    )
    const bottomSheet = await category.openProduct(identifiers.productWithRelatedNonUniqueCombo)
    await bottomSheet.assertImage()
  })

  it('yalavka-523: Замена товара в комбо', async function () {
    const category = new CategoryPage(this)
    await category.openCategoryPage(
      {
        categoryId: identifiers.categoryWithBundles,
      },
      {
        cookies: comboTestsCookies,
      },
    )
    const bottomSheet = await category.openProduct(identifiers.productWithRelatedSingleSelectionGroupCombo)
    const bundleBottomSheet = await bottomSheet.clickOnAvailableBundleItem(0)
    await bundleBottomSheet.clickReplaceButton(0)
    await bottomSheet.assertImage({state: 'bundle-replace-sheet-default'})
    await bundleBottomSheet.selectBundlePart('6c5a74a2fe8b40858547aa30b4494000000100010001')
    await bottomSheet.assertImage({state: 'bundle-replace-sheet-selected'})
    await bundleBottomSheet.confirmBundleReplace()
    await bundleBottomSheet.waitTillPriceIs(389)
    await bottomSheet.assertImage({state: 'bundle-replace-confirmed'})
  })

  it('yalavka-541: Клик по информеру тегов в описании товара', async function () {
    const category = new CategoryPage(this)

    await category.openCategoryPage()
    const mockServerApi = await getMockServerApiUrl(this.browser)
    const fakeImage = `${mockServerApi}/fake-images/get-bunker/998550/a79be3f1a7e48ebca29fea15b846d208ee3e31f9/orig`

    await category.openCategoryPage(
      {
        categoryId: identifiers.categoryBase,
      },
      {
        cookies: {
          ...makeExperimentsCookies({
            'lavka-frontend_product_tags_informer': {
              enabled: true,
              pictureUrl: fakeImage,
            },
          }),
        },
      },
    )
    const bottomSheet = await category.openProduct(identifiers.productBase)
    await bottomSheet.scrollToSection('description')
    await bottomSheet.assertImage({state: 'tags-informer'})
    await bottomSheet.clickTagsInformer()
    await category.waitForTagsBottomSheetExists()
    await bottomSheet.assertImage({state: 'tags-bottom-sheet'})
  })
})
