import {LAVKA_APP, TEST_CHAT_ID} from './constants'
import {IosCheckReleasesOptions, OptionItem} from './types'

const LAVKA_IOS: OptionItem = {
  chatIds: [TEST_CHAT_ID],
  appId: LAVKA_APP.id,
  appName: LAVKA_APP.name,
  startTime: '2022-02-04T02:19:59-08:00',
  secrets: {
    issuerId: 'ios.app-store-api.issuer-id',
    keyId: 'ios.app-store-api.key-id',
    keyContent: 'ios.app-store-api.key-content',
  },
}

export const IOS_CHECK_RELEASES_CONFIG_TEST: IosCheckReleasesOptions = [LAVKA_IOS]
