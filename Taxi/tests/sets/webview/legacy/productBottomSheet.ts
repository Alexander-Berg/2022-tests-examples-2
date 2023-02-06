import {baseCategoryId, baseProductId} from '../../../constants/common'
import {categoryProductItemClick} from '../../../helpers'
import {mkTestId} from '../../../utils/mkTestId'

describe('NO TESTCASE: open product bottom sheet scenarios', async function () {
  it('NO TESTCASE: should open product bottom sheet', async function () {
    await this.browser.openPage(`/?group=0f1846f41ac8453680a175023a77fae3&category=${baseCategoryId}`)
    await categoryProductItemClick(this, {productId: baseProductId})
    // TODO вынести в отдельную команду waitForBottomSheetOpened
    await this.browser.waitForElementExists(mkTestId('product-card-bottom-sheet'))
    await this.browser.assertImage(mkTestId('product-card-bottom-sheet'))
  })
})
