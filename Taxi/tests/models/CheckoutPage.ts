import {WaitForOptions} from 'webdriverio/build/types'

import {
  AssertImageOptions,
  mkDataLoading,
  ScrollToElementOptions,
  TypeIntoOptions,
  mkAriaDisabled,
  mkDataChecked,
  mkDataDisabled,
  mkDataItemId,
  mkDataItemType,
  mkDataValue,
  mkTestId,
} from '@lavka/tests'

import {BasePage, OpenPageOptions} from './BasePage'

const getPlusRadioButton = (buttonType: 'charge' | 'gain') => {
  const radioButtonSelector = `${mkTestId('radio-button')} ${mkDataValue(buttonType)}`
  return `${mkTestId('checkout-cashback')} ${radioButtonSelector}`
}

export class CheckoutPage extends BasePage {
  private layoutTestId = mkTestId('checkout-page-layout')
  private contentTestId = mkTestId('checkout-page-content')
  private couponListId = mkTestId('coupon-list')
  private tipsListId = mkTestId('tips-list')
  private addressBottomSheetId = mkTestId('address-bottom-sheet')
  private promocodeBottomSheetId = mkTestId('promocode-bottom-sheet')
  private searchAddressBottomSheetId = mkTestId('search-address-bottom-sheet')
  private selectPaymentMethodBottomSheetId = mkTestId('select-payment-method-bottom-sheet')

  async openPage(options?: OpenPageOptions) {
    await this.open('/checkout', options)
    await this.waitForPageLoaded()
  }

  async waitForPageLoaded() {
    await this.browser.waitForElementExists(this.layoutTestId)
    await this.browser.waitForElementExists(this.contentTestId)
  }

  async assertImage(options?: AssertImageOptions, checkoutOptions?: {waitForCartButtonActive?: boolean}) {
    if (checkoutOptions?.waitForCartButtonActive) {
      await this.waitForCartButtonActive()
    }
    await this.browser.assertImage(this.layoutTestId, options)
  }

  async scrollToLayoutPageBlock(blockId: string, options?: ScrollToElementOptions) {
    await this.browser.scrollToElement(`${this.layoutTestId} ${mkDataItemId(blockId)}`, options)
  }

  async waitForLayoutPageBlockExists(blockId: string) {
    await this.browser.waitForElementExists(`${this.layoutTestId} ${mkDataItemId(blockId)}`)
  }

  async clickCashbackRadioToggle(buttonType: 'charge' | 'gain') {
    await this.waitForCartButtonActive()
    await this.browser.waitForElementAndClick(getPlusRadioButton(buttonType))
  }

  async waitForCashbackRadioText(text: string, buttonType: 'charge' | 'gain') {
    const buttonTextElement = `${getPlusRadioButton(buttonType)} ${mkTestId('plus-points-value')}`
    await this.browser.waitForElementText(buttonTextElement, text)
  }

  async waitAndClickPromocodeCoupon(promocodeId: string) {
    await this.waitForCartButtonActive()
    await this.browser.waitForElementAndClick(`${this.couponListId} ${mkDataItemId(promocodeId)}`)
  }

  async scrollCouponListToCoupon(couponId: string) {
    await this.browser.scrollToElement(`${this.couponListId}`)
    await this.browser.scrollToElement(`${this.couponListId} ${mkDataItemId(couponId)}`, {
      scrollAxis: 'horizontal',
      scrollableContainerSelector: this.couponListId,
    })
  }

  async waitForCouponExists(couponId: string) {
    await this.browser.waitForElementExists(`${this.couponListId} ${mkDataItemId(couponId)}`)
  }

  async assertCouponValue(couponId: string, value: 'false' | 'true') {
    await this.waitForCartButtonActive()
    await this.browser.waitForElementExists(`${this.couponListId} ${mkDataItemId(couponId)}${mkDataValue(value)}`)
  }

  async waitForSelectedPaymentMethod(type: string) {
    await this.browser.waitForElementExists(`${mkTestId('payment-method')} ${mkDataItemType(type)}`)
  }

  async waitAndClickForSelectedPaymentMethod(options?: {waitForCartButtonActive?: boolean}) {
    if (options?.waitForCartButtonActive) {
      await this.waitForCartButtonActive()
    }
    await this.browser.waitForElementAndClick(`${mkTestId('payment-method ui-payment-item')}${mkAriaDisabled('false')}`)
    await this.waitForSelectPaymentMethodBottomSheet()
  }

  async waitForSelectPaymentMethodBottomSheet(options?: WaitForOptions) {
    await this.browser.waitForElementExists(this.selectPaymentMethodBottomSheetId, options)
  }

  async closeBottomSheetPaymentMethods() {
    await this.browser.waitForElementAndClick(`${this.selectPaymentMethodBottomSheetId} ${mkTestId('close-button')}`)
    await this.waitForSelectPaymentMethodBottomSheet({reverse: true})
  }

  async selectPaymentMethodInBottomSheet(
    props: {id: string} | {type: string},
    options?: {skipWaitingForCloseBottomSheet: boolean},
  ) {
    let itemSelector: string | undefined = undefined
    if ('id' in props) {
      itemSelector = mkDataItemId(props.id)
    }
    if ('type' in props) {
      itemSelector = mkDataItemType(props.type)
    }
    await this.browser.waitForElementAndClick(`${this.selectPaymentMethodBottomSheetId} ${itemSelector}`)
    if (!options?.skipWaitingForCloseBottomSheet) {
      await this.waitForSelectPaymentMethodBottomSheet({reverse: true})
    }
  }

  async clickAvailablePayButton() {
    await this.browser.waitForElementAndClick(`${mkTestId('cart-button')}${mkDataDisabled('false')}`)
  }

  async waitAndClickAddressSwitcher(name: string) {
    await this.browser.waitForElementAndClick(mkTestId(`${name} switcher`), {waitForNotActiveAfterClick: true})
  }
  async waitAndClickAddressCheckbox(name: string) {
    await this.browser.waitForElementAndClick(mkTestId(`${name} checkbox`))
  }

  async typeTextToAddressField(name: string, text: string, options?: TypeIntoOptions) {
    await this.browser.typeText(`${mkDataItemId('address')} ${mkTestId(name)} input`, text, options)
  }

  async typeTextToCommentField(text: string, options?: TypeIntoOptions) {
    await this.browser.typeText(`${mkTestId('comment')} textarea`, text, options)
  }

  async waitAndClickPromocodeField() {
    await this.waitForCartButtonActive()
    await this.browser.waitForElementAndClick(mkTestId('promocode'))
    await this.waitForPromocodeBottomSheetOpened()
  }

  async waitForPromocodeBottomSheetOpened(options?: WaitForOptions) {
    await this.browser.waitForElementExists(this.promocodeBottomSheetId, options)
  }

  async confirmPromocode(options?: {waitForBottomSheetClosed?: boolean}) {
    await this.browser.waitForElementAndClick(`${this.promocodeBottomSheetId} ${mkTestId('confirm-button')}`)
    if (options?.waitForBottomSheetClosed) {
      await this.waitForPromocodeBottomSheetOpened({reverse: true})
    }
  }

  async clickRemovePromocodeButton(options?: {waitForBottomSheetClosed?: boolean}) {
    await this.browser.waitForElementAndClick(`${this.promocodeBottomSheetId} ${mkTestId('trash-button')}`)
    if (options?.waitForBottomSheetClosed) {
      await this.waitForPromocodeBottomSheetOpened({reverse: true})
    }
  }

  async typePromocodeText(code: string, options?: TypeIntoOptions) {
    await this.browser.typeText(`${this.promocodeBottomSheetId} input`, code, options)
  }

  async waitForDeliveryAddressBottomSheet(options?: WaitForOptions) {
    await this.browser.waitForElementExists(this.addressBottomSheetId, options)
  }

  async waitAndClickAddressField() {
    await this.waitForCartButtonActive()
    await this.browser.waitForElementAndClick(mkTestId('delivery-address'))
  }

  async waitAndClickAddressFieldFromBottomSheet() {
    await this.waitForCartButtonActive()
    await this.browser.waitForElementAndClick(`${this.addressBottomSheetId} ${mkTestId('address')}`)
  }

  async waitForSearchAddressBottomSheet(options?: WaitForOptions) {
    await this.browser.waitForElementExists(`${this.searchAddressBottomSheetId}${mkDataLoading('false')}`, options)
  }

  async typeAddressBottomSheetAddressFieldText(fieldName: string, text: string, options?: TypeIntoOptions) {
    await this.browser.typeText(`${this.addressBottomSheetId} ${mkTestId(fieldName)} input`, text, options)
  }
  async typeSearchBottomSheetSearchAddressText(text: string, options?: TypeIntoOptions) {
    await this.browser.typeText(`${this.searchAddressBottomSheetId} ${mkTestId('search-input')}`, text, options)
  }

  async waitForFoundItemInSearchBottomSheet({itemNum, textLike}: {itemNum: number; textLike: string}) {
    const textSelector = `${this.searchAddressBottomSheetId} ${mkTestId(`search-item-${itemNum} title`)}`
    await this.browser.waitForElementText(textSelector, textLike, {searchType: 'like'})
  }

  async waitForNotFoundAddressMessageExists() {
    await this.browser.waitForElementExists(`${this.searchAddressBottomSheetId} ${mkTestId('not-found-address-item')}`)
  }

  async clickEraseSearchBottomSheetSearchField() {
    await this.browser.waitForElementAndClick(`${this.searchAddressBottomSheetId} ${mkTestId('clear-search-button')}`)
  }

  async clickConfirmAddressButton() {
    await this.browser.waitForElementAndClick(mkTestId('confirm-button'))
    await this.waitForSearchAddressBottomSheet({reverse: true})
  }

  async clickSearchAddressItem(itemNum: number) {
    await this.browser.waitForElementAndClick(
      `${this.searchAddressBottomSheetId} ${mkTestId(`search-item-${itemNum}`)}`,
    )
  }

  async clickTipsVariant(value: string) {
    await this.browser.waitForElementAndClick(`${this.tipsListId} ${mkDataValue(value)}`)
    await this.browser.waitForElementExists(`${this.tipsListId} ${mkDataValue(value)}${mkDataChecked('true')}`)
  }

  async clickSaveTipsCheckbox() {
    await this.browser.waitForElementAndClick(mkDataItemId('remember-tips-checkbox'))
  }
}
