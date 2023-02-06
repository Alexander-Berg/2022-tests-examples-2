import {TestDefinitionCallbackCtx} from 'hermione'
import {WaitForOptions} from 'webdriverio/build/types'

import {GroceryOrderStatus} from '@lavka/api-typings/uservices/grocery-orders/definitions'
import {identifiers} from '@lavka/constants'
import {
  AssertImageOptions,
  mkDataItemId,
  mkDataValueStatus,
  mkTestId,
  modifyFutureBackendResponses,
  WaitForElementExistsOptions,
} from '@lavka/tests'

import {BasePage, OpenPageOptions} from './BasePage'

interface OpenPageParams {
  orderId: string
  skipWaitForLoading?: boolean
}

interface Options {
  useWebMapLayout: boolean
}

export class TrackingPage extends BasePage {
  private readonly useWebMapLayout?: boolean

  private pageBaseLayout = mkTestId(identifiers.pageTrackingLayout)
  private pageMapLayout = mkTestId(identifiers.pageTrackingMapLayout)
  private bottomSheetTrackingStatusSection = mkTestId('bottom-sheet-tracking-status-section')

  constructor(ctx: TestDefinitionCallbackCtx, options?: Options) {
    super(ctx)
    /* в веб картах используется другой layout, эксперименты проставляем в тестах индивидуально */
    this.useWebMapLayout = options?.useWebMapLayout
  }

  async openPage(params: OpenPageParams, options?: OpenPageOptions) {
    await this.open(`/order/${params.orderId}`, options)
    if (!params.skipWaitForLoading) {
      await this.waitForLayout()
    }
  }

  async waitForMap() {
    await this.browser.waitForImages({testId: 'ya-map-marker'})
  }

  async waitAndClickCloseButtonButton() {
    await this.browser.waitForElementAndClick(mkTestId('close-bottom-button'))
  }

  async waitForLayout() {
    if (this.useWebMapLayout) {
      await this.browser.waitForElementExists(this.pageMapLayout)
      await this.waitForMap()
    } else {
      await this.browser.waitForElementExists(this.pageBaseLayout)
    }
  }

  async waitForStatus(status: GroceryOrderStatus) {
    await this.browser.waitForElementExists(`${this.bottomSheetTrackingStatusSection}${mkDataValueStatus(status)}`)
    if (this.useWebMapLayout) {
      /* у карты происходят спецэффекты смещения (по какой-то причине) ждём немного */
      await this.browser.pause(500)
    }
  }

  async assertImage(options?: AssertImageOptions) {
    await this.assertBodyImage(options)
  }

  async scrollToPageSection(sectionName: string) {
    if (this.useWebMapLayout) {
      await this.browser.scrollToElement(`${mkTestId('page-block-item')}${mkDataItemId(sectionName)}`, {
        scrollableContainerSelector: mkTestId('scrollable-outer-content'),
      })
    } else {
      await this.browser.scrollToElement(`${mkTestId('page-block-item')}${mkDataItemId(sectionName)}`)
    }
  }

  async clickToolbarBackButton() {
    await this.browser.waitForElementAndClick(mkTestId('back-button'))
  }

  async testAllTrackingStatuses() {
    await modifyFutureBackendResponses(this, {
      'grocery_orders[0]:status': 'assembling',
    })
    await this.waitForStatus('assembling')
    await this.assertImage({state: 'status-changed-to-assembling'})
    await modifyFutureBackendResponses(this, {
      'grocery_orders[0]:status': 'assembled',
    })
    await this.waitForStatus('assembled')
    await this.assertImage({state: 'status-changed-to-assembled'})
    await modifyFutureBackendResponses(this, {
      'grocery_orders[0]:status': 'delivering',
    })
    await this.waitForStatus('delivering')
    await this.assertImage({state: 'status-changed-to-delivering'})
    await modifyFutureBackendResponses(this, {
      'grocery_orders[0]:status': 'delivery_arrived',
    })
    await this.waitForStatus('delivery_arrived')
    await this.assertImage({state: 'status-changed-to-delivery_arrived'})
    await modifyFutureBackendResponses(this, {
      'grocery_orders[0]:status': 'closed',
      'grocery_orders[0]:resolution': 'succeeded',
    })
    await this.browser.waitForElementExists(mkTestId('tracking-steps'))
    await this.waitForStatus('closed')
    await this.assertImage({state: 'status-changed-to-closed'})
  }

  async clickStatusButton() {
    await this.browser.waitForElementAndClick(mkTestId('tracking-status-button'))
  }

  async clickActionButton(id: string) {
    await this.browser.waitForElementAndClick(mkTestId(id))
    if (id === 'order-details') {
      /* при клике задевается соседняя кнопка справа, ожидаем исчезновение active эффекта */
      await this.waitForActionButtonNonActive('another-order')
    }
  }

  async waitForActionButtonNonActive(id: string) {
    await this.browser.waitForElementExists(`${mkTestId(id)} button`, {waitForNotActiveAfterClick: true})
  }

  async clickCancelOrder() {
    await this.browser.waitForElementAndClick(mkTestId('footer-button'))
  }

  async confirmAskCancelOrder() {
    await this.browser.waitForElementAndClick(mkTestId('cancel-order-modal confirm-button'))
  }

  async confirmSuccessCancelOrder() {
    await this.browser.waitForElementAndClick(mkTestId('canceled-order-modal confirm-button'))
  }

  async waitForFailedCancelOrderModal() {
    await this.browser.waitForElementExists(mkTestId('failed-cancel-order-modal'))
  }
  async waitForSuccessCancelOrderModal(options?: WaitForOptions) {
    await this.browser.waitForElementExists(mkTestId('canceled-order-modal'), options)
  }
  async waitAndClickSupplyInfo() {
    await this.browser.waitForElementAndClick(
      `${mkTestId('page-block-item')}${mkDataItemId('address')} ${mkTestId('supply-info-item')}`,
    )
  }

  async waitForSupplyInfoBottomSheet(options?: WaitForElementExistsOptions) {
    await this.browser.waitForElementExists(mkTestId('supply-info-bottom-sheet'), options)
  }
}
