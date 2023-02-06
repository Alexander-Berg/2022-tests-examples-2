import {baseCategoryId} from '../../../constants/common'
import {backHeaderButtonClick, categoryCardClick} from '../../../helpers'
import {mkTestId} from '../../../utils/mkTestId'

describe('NO TESTCASE: open main page scenarios', async function () {
  it('NO TESTCASE: should render main page', async function () {
    await this.browser.openPage('/')
    await this.browser.waitForElementExists(mkTestId('main-page-layout'))
    await this.browser.assertImage(mkTestId('main-page-layout'))
  })

  it('NO TESTCASE: should open first category on main page and correct returned back', async function () {
    await this.browser.openPage('/')
    await categoryCardClick(this, {categoryId: baseCategoryId})
    await backHeaderButtonClick(this)
    await this.browser.assertImage(mkTestId('main-page-layout'))
  })
})
