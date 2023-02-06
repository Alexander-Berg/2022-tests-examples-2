import {identifiers} from '@lavka/constants'
import {
  makeExperimentsCookies,
  makeFutureBackendResponsesCookie,
  modifyFutureBackendResponses,
  waitAndAssertClientRequest,
} from '@lavka/tests'

import {CheckoutPage, VerificationCardBottomSheet, NewCardBottomSheet, Web3dsFrame} from '../../models'

describe('Привязка/Верификация', async function () {
  it('yalavka-491: Успешная привязка карты (web 3ds) и оплата со страницы чекаута, когда нет способа оплаты', async function () {
    const newCardBottomSheet = new NewCardBottomSheet(this)
    const verificationCardBottomSheet = new VerificationCardBottomSheet(this)
    const checkoutPage = new CheckoutPage(this)
    const web3dsFrame = new Web3dsFrame(this)
    await checkoutPage.openPage({
      cookies: {
        cardVerifyStrategy: 'web3ds',
        useCartService: 'true',
        cartRetrieveId: identifiers.cartRetrieveEpsilon,
        ...makeExperimentsCookies({
          'lavka-frontend_web-payment-method': {
            paymentsWithCartBindingEnabled: true,
            cardScannerEnabled: true,
          },
        }),
        ...makeFutureBackendResponsesCookie({'list-payment-methods:payment_methods': []}),
      },
    })
    await checkoutPage.waitForCartButtonActive()
    await checkoutPage.scrollToLayoutPageBlock('payment')
    await checkoutPage.assertImage({state: 'order-button-allowed'})
    await checkoutPage.clickAvailablePayButton()
    await newCardBottomSheet.waitForExists()
    await checkoutPage.assertImage({state: 'add-new-card-bottom-sheet-opened'})
    await newCardBottomSheet.typeTextToField('card-number-field', '5300 0042 0673 4616')
    await newCardBottomSheet.typeTextToField('card-expires-field', '0525')
    await newCardBottomSheet.typeTextToField('card-cvv-field', '777')
    await checkoutPage.assertImage({state: 'fields-filled'})
    await newCardBottomSheet.clickSubmit()
    await verificationCardBottomSheet.waitForExists()
    await web3dsFrame.waitForLoaded()
    await checkoutPage.assertImage({state: 'web-3ds-loaded'})
    await modifyFutureBackendResponses(this, {'card-antifraud:status': 'success'})
    await modifyFutureBackendResponses(this, {
      'list-payment-methods:payment_methods': [
        {
          type: 'card',
          name: 'VISA',
          id: identifiers.cardIdAlpha,
          card_country: 'RUS',
          bin: '400000',
          currency: 'RUB',
          system: 'VISA',
          number: '530000****4616',
          available: true,
          availability: {available: true, disabled_reason: ''},
        },
      ],
    })
    await verificationCardBottomSheet.waitForExists({reverse: true})
    await waitAndAssertClientRequest(this, 'cart/v1/set-payment', {
      haveBeenCalledTimes: 1,
      matchDeepInclude: {
        payment_method: {
          id: identifiers.cardIdAlpha,
          type: 'card',
          meta: {
            card: {
              issuer_country: 'RUS',
            },
          },
        },
      },
    })
    await checkoutPage.assertImage({state: 'card-added-and-selected'})
  })
})
