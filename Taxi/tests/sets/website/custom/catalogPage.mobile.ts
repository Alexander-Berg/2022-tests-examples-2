import { identifiers } from '@lavka/constants'
import { makeExperimentsCookies } from '@lavka/tests'

import { CatalogPageMobile } from '../../../models'

describe('Custom: Каталог (Mobile)', function () {
  it('Открытие заглушки при отключенном экспе мобильной лавки', async function () {
    const catalogPage = new CatalogPageMobile(this)
    await catalogPage.openPage({
      waitForStub: true,
      cookies: {
        ...makeExperimentsCookies({
          desktop_mobile: {
            enabled: false,
          },
        }),
      },
    })
    await catalogPage.assertImage({ state: 'page-opened' })
  })
  it('Открытие каталога без адреса', async function () {
    const catalogPage = new CatalogPageMobile(this)
    await catalogPage.openPage({
      cookies: {
        useLegacyAddressApi: 'true',
      },
    })
    await catalogPage.assertImage({ state: 'page-opened' })
  })
  it('Открытие каталога с адресом', async function () {
    const catalogPage = new CatalogPageMobile(this)
    await catalogPage.openPage({
      cookies: {
        lastGeoUri: identifiers.geoPointMarksistskaya,
      },
    })
    await catalogPage.assertImage({ state: 'page-opened' })
  })
  it('Открытие сетки товаров с разным и большим количеством категорий', async function () {
    const catalogPage = new CatalogPageMobile(this)
    await catalogPage.openPage({
      cookies: {
        layoutId: identifiers.layoutDeltaId,
      },
    })
    await catalogPage.assertImage({ state: 'page-opened', stretch: true })
  })
})
