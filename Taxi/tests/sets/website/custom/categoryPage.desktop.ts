// TODO: сделать абсолютные импорты https://st.yandex-team.ru/LAVKAFRONT-4906

import { identifiers } from '@lavka/constants'

import { CategoryPageDesktop } from '../../../models'

describe('Custom: Страница категории', function () {
  it('Открытие страницы категории с выбранным адресом по last geo', async function () {
    const categoryPage = new CategoryPageDesktop(this)
    await categoryPage.openPage(identifiers.categoryBase, {
      cookies: {
        lastGeoUri: identifiers.geoPointMarksistskaya,
      },
    })
    await categoryPage.assertImage()
  })
})
