import {v4} from 'uuid'

import {CartUpdateRequest} from '@lavka/api-typings/uservices/grocery-cart/api/update'
import {identifiers} from '@lavka/constants'

import {cartUpdateResultController} from '../cartUpdateController'

const position = {location: [37.6424736597268, 55.735525020209344]}
const STAND_ID = 'DEFAULT_STAND_ID'

describe('cartUpdateResultController', () => {
  const PRODUCT_PARCEL_1 = identifiers.productParcel1
  const PRODUCT_UPSALE_ALPHA = identifiers.productUpsaleAlpha

  it('Пустой запрос', () => {
    const body: CartUpdateRequest = {
      cart_id: v4(),
      position: {
        location: [0, 0],
      },
      items: [],
    }
    const res = cartUpdateResultController({
      reqBody: body,
      standId: STAND_ID,
    })

    expect(res.status).toBe('OK')
    expect(res.data?.items).toEqual([])
  })
  //
  it('Посылка с нулевой стоимостью', () => {
    const body: CartUpdateRequest = {
      cart_id: v4(),
      position,
      items: [
        {
          id: PRODUCT_PARCEL_1,
          quantity: '1',
          price: '0',
          currency: 'RUB',
        },
      ],
    }
    const res = cartUpdateResultController({
      reqBody: body,
      standId: STAND_ID,
    })

    expect(res.status).toBe('OK')
    expect(res.data?.items).toHaveLength(1)
    expect(res.data?.items[0].quantity).toEqual('1')
    expect(res.data?.items[0].price).toEqual('0')
    expect(res.data?.items[0].id).toEqual(PRODUCT_PARCEL_1)
  })
  it('Можно добавить товар из апсейла', () => {
    const body: CartUpdateRequest = {
      cart_id: v4(),
      position,
      items: [
        {
          id: PRODUCT_UPSALE_ALPHA,
          quantity: '1',
          price: '55',
          currency: 'RUB',
        },
      ],
    }
    const res = cartUpdateResultController({
      reqBody: body,
      standId: STAND_ID,
    })

    expect(res.status).toBe('OK')
    expect(res.data?.items).toHaveLength(1)
    expect(res.data?.items[0].quantity).toEqual('1')
    expect(res.data?.items[0].price).toEqual('55')
    expect(res.data?.items[0].id).toEqual(PRODUCT_UPSALE_ALPHA)
  })

  it('Можно добавить товар из апсейла, после этого добавить посылку', () => {
    const body1: CartUpdateRequest = {
      cart_id: v4(),
      position,
      items: [
        {
          id: PRODUCT_UPSALE_ALPHA,
          quantity: '1',
          price: '55',
          currency: 'RUB',
        },
      ],
    }

    cartUpdateResultController({
      reqBody: body1,
      standId: STAND_ID,
    })

    const body2: CartUpdateRequest = {
      cart_id: body1.cart_id,
      position,
      items: [
        {
          id: PRODUCT_PARCEL_1,
          quantity: '1',
          price: '0',
          currency: 'RUB',
        },
      ],
    }

    const res = cartUpdateResultController({
      reqBody: body2,
      standId: STAND_ID,
    })

    expect(res.status).toBe('OK')
    expect(res.data?.items).toHaveLength(2)
    expect(res.data?.items[0].quantity).toEqual('1')
    expect(res.data?.items[0].price).toEqual('55')
    expect(res.data?.items[0].id).toEqual(PRODUCT_UPSALE_ALPHA)
    expect(res.data?.items[1].quantity).toEqual('1')
    expect(res.data?.items[1].price).toEqual('0')
    expect(res.data?.items[1].id).toEqual(PRODUCT_PARCEL_1)
  })
  //
  it('Можно добавить посылку(пустой cart_id), после этого добавить товар из апсейла', () => {
    const body1: CartUpdateRequest = {
      position,
      items: [
        {
          id: PRODUCT_PARCEL_1,
          quantity: '1',
          price: '0',
          currency: 'RUB',
        },
      ],
    }

    const body2: CartUpdateRequest = {
      position,
      items: [
        {
          id: PRODUCT_UPSALE_ALPHA,
          quantity: '1',
          price: '55',
          currency: 'RUB',
        },
      ],
    }

    const res1 = cartUpdateResultController({
      reqBody: body1,
      standId: STAND_ID,
    })
    const res = cartUpdateResultController({
      reqBody: {
        ...body2,
        cart_id: res1.data?.cart_id,
      },
      standId: STAND_ID,
    })

    expect(res.status).toBe('OK')
    expect(res.data?.items).toHaveLength(2)
    expect(res.data?.items[0].quantity).toEqual('1')
    expect(res.data?.items[0].price).toEqual('0')
    expect(res.data?.items[0].id).toEqual(PRODUCT_PARCEL_1)
    expect(res.data?.items[1].quantity).toEqual('1')
    expect(res.data?.items[1].price).toEqual('55')
    expect(res.data?.items[1].id).toEqual(PRODUCT_UPSALE_ALPHA)
  })

  it('Товар из апсейла можно добавить, затем удалить', () => {
    const body1: CartUpdateRequest = {
      cart_id: v4(),
      position,
      items: [
        {
          id: PRODUCT_UPSALE_ALPHA,
          quantity: '1',
          price: '55',
          currency: 'RUB',
        },
      ],
    }

    const res1 = cartUpdateResultController({
      reqBody: body1,
      standId: STAND_ID,
    })

    expect(res1.status).toBe('OK')
    expect(res1.data?.items).toHaveLength(1)
    expect(res1.data?.items[0].quantity).toEqual('1')
    expect(res1.data?.items[0].price).toEqual('55')
    expect(res1.data?.items[0].id).toEqual(PRODUCT_UPSALE_ALPHA)

    const body2: CartUpdateRequest = {
      cart_id: res1.data?.cart_id,
      position,
      items: [
        {
          id: PRODUCT_UPSALE_ALPHA,
          quantity: '0',
          price: '55',
          currency: 'RUB',
        },
      ],
    }

    const res2 = cartUpdateResultController({
      reqBody: body2,
      standId: STAND_ID,
    })

    expect(res2.status).toBe('OK')
    expect(res2.data?.items).toHaveLength(0)
  })
})
