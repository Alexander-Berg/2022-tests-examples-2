import {baseCategoryId} from '../../../constants/common'
import {openCategoryPage} from '../../../helpers'
import {mkTestId} from '../../../utils/mkTestId'

describe('NO TESTCASE: open category page scenarios', async function () {
  it('NO TESTCASE: should correct open category page', async function () {
    await openCategoryPage(this, {categoryId: baseCategoryId})
    await this.browser.waitForElementExists(mkTestId('category-page-layout'))
    await this.browser.assertImage(mkTestId('category-page-layout'))
  })
})
