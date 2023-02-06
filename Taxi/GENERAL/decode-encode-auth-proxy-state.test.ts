import type { AuthProxyState } from 'types/auth'
import { decodeAuthProxyState } from 'utils/decode-auth-proxy-state'
import { encodeAuthProxyState } from 'utils/encode-auth-proxy-state'

interface ValidCase {
  state: AuthProxyState
  str: string
}

const decodeEncodeValidCases: ValidCase[] = [
  {
    state: {
      authType: 'authorized',
      taxiUserId: 'taxiUserId',
      passportPayloadHash: 123456789,
      shouldConfirmPhone: true,
    },
    str: 'authorized:taxiUserId:123456789:true',
  },
  {
    state: {
      authType: 'notAuthorized',
      taxiUserId: 'taxiUserId',
      passportPayloadHash: 123456789,
      shouldConfirmPhone: true,
    },
    str: 'notAuthorized:taxiUserId:123456789:true',
  },
  {
    state: {
      authType: 'authorized',
      taxiUserId: 'taxiUserId',
      passportPayloadHash: 123456789,
      shouldConfirmPhone: false,
    },
    str: 'authorized:taxiUserId:123456789:false',
  },
]

const decodeValidCases: ValidCase[] = [
  {
    str: 'str:taxiUserId:123456789:true',
    state: {
      authType: 'notAuthorized',
      taxiUserId: 'taxiUserId',
      passportPayloadHash: 123456789,
      shouldConfirmPhone: true,
    },
  },
  {
    str: 'authorized:taxiUserId:str:true',
    state: {
      authType: 'authorized',
      taxiUserId: 'taxiUserId',
      passportPayloadHash: 0,
      shouldConfirmPhone: true,
    },
  },
  {
    str: 'authorized:taxiUserId:123456789:str',
    state: {
      authType: 'authorized',
      taxiUserId: 'taxiUserId',
      passportPayloadHash: 123456789,
      shouldConfirmPhone: false,
    },
  },
  {
    str: 'authorized:taxiUserId:123456789',
    state: {
      authType: 'authorized',
      taxiUserId: 'taxiUserId',
      passportPayloadHash: 123456789,
      shouldConfirmPhone: false,
    },
  },
  {
    str: 'authorized:taxiUserId',
    state: {
      authType: 'authorized',
      taxiUserId: 'taxiUserId',
      passportPayloadHash: 0,
      shouldConfirmPhone: false,
    },
  },
]

const invalidStr: string[] = ['authorized:', 'authorized']

describe('Decode and encode auth proxy state tests', () => {
  test.each(decodeEncodeValidCases)('Encode $state', ({ state, str }) => {
    const actual = encodeAuthProxyState(state)
    expect(actual).toEqual(str)
  })

  test.each([...decodeEncodeValidCases, ...decodeValidCases])('Decode $str', ({ state, str }) => {
    const actual = decodeAuthProxyState(str)
    expect(actual).toEqual(state)
  })

  test.each(invalidStr)('Decode %s', (str) => {
    const actual = decodeAuthProxyState(str)
    expect(actual).toBeUndefined()
  })
})
