import hitSelectMiddlewareCreator from '@player2/store/middleware/hit-select-middleware'
import fakeStore from '@test/fakes/fakeStore'
import { fetchHit, FETCH_HIT } from '@player2/store/actions/api'
import { selectCurrentHit, setCurrentHit } from '@player2/store/actions/currentHit'

describe('Hit select middleware', () => {
  const middleware = hitSelectMiddlewareCreator(fakeStore as any)(fakeStore.next)
  it('Fetches hit if needed and returns promise with the result', () => {
    fakeStore.reset()
    fakeStore.setReturnValues({
      [FETCH_HIT]: () => Promise.resolve({data: 'data'}),
    })
    fakeStore.setState({
      api: {
        hitsCache: {},
      },
      currentHit: {
        data: 'previousData',
      },
    })

    const resultPromise = middleware(selectCurrentHit(0)).then((result: any) => {
      return {
        dispatch: fakeStore.actionsDispatched,
        next: fakeStore.actionsProceededToNext,
        result,
      }
    })

    expect(resultPromise).resolves.toEqual({
      dispatch: [fetchHit(0), setCurrentHit({data: 'data'})],
      next: [selectCurrentHit(0)],
      result: {data: 'data'},
    })
  })
})