import onActionMiddleware, { subscribe, unsubscribe } from '@player2/store/middleware/on-action-middleware'
import fakeStore from '@test/fakes/fakeStore'

describe('on action middleware', () => {
  const type = 'SOME_TYPE'
  const otherType = 'SOME_OTHER_TYPE'
  const callback = jest.fn().mockName('callback')
  const middleware = onActionMiddleware(fakeStore as any)(fakeStore.next)

  it('subscribes to action and calls it', () => {
    subscribe(type, callback)
    middleware({type} as any)
    middleware({type: otherType} as any)
    unsubscribe(type, callback)
    middleware({type} as any)
    expect(callback).toHaveBeenCalledTimes(1)
  })
})
