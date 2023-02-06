import {readMockRequest} from '../../tests/mock-request'
import {providersRegistry} from '../lib/registry'

import * as cartClient from './client'

const position = {location: [37.657268912456246, 55.739108244335085]}
const item1 = {
  id: '2cf37f33e35a44f5abc77d9ed96b39ba000300010000',
  quantity: '1',
  price: '239',
  currency: 'RUB',
}
const item2 = {
  id: '325d145b9b8c495fb0e0a5c07e1c37fd000100010001',
  quantity: '1',
  price: '209',
  currency: 'RUB',
}
const item3 = {
  id: '17eff77507324f74b63d28f327203ad1000300010000',
  quantity: '1',
  price: '149',
  currency: 'RUB',
}

beforeEach(() => {
  providersRegistry.clear()
})

describe('conflict resolver', () => {
  it('update', async () => {
    cartClient.initialize({requestFn: readMockRequest(expect.getState().currentTestName)})

    const cart1 = await cartClient.update({items: [item1], position})
    await cartClient.update({cart_id: cart1.cart_id, cart_version: cart1.cart_version, items: [item2], position})
    const cart3 = await cartClient.update({
      cart_id: cart1.cart_id,
      cart_version: cart1.cart_version,
      items: [item3],
      position,
    })

    expect(cart3.cart_version).toEqual(3)
    expect(cart3.cart_id).toEqual('8a5eca6a-05f8-4416-a023-ae61ecb60d53')
    expect(cart3.items.map(({id}) => id)).toEqual([item1.id, item2.id, item3.id])
  })
})
