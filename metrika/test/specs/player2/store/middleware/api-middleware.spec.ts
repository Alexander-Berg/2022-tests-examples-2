import fakeStore from '@test/fakes/fakeStore'
import fakeHitApi from '@test/fakes/fakeHitApi'
import apiMiddlewareCreator, {
  resetRequestsCache
} from '@player2/store/middleware/api-middleware'
import {
  FETCH_HIT,
  GET_VISIT_INFO,
  SET_COMMENT,
  SET_FAVORITE,
  FETCH_HITS_LIST,
  fetchHit,
  getVisitInfo,
  fetchHitsList,
  setComment,
  setFavorite,
  apiSuccess,
  apiError,
} from '@player2/store/actions/api'

describe('Api middleware', () => {
  const actionsToCheck = [
    fetchHit(),
    getVisitInfo(),
    fetchHitsList(),
  ]

  const middleware = apiMiddlewareCreator(
    fakeHitApi as any,
    {offset: 0, createProcessor: null} as any,
    () => undefined
  )
    (fakeStore as any)
    (fakeStore.next)

  const reset = (success: boolean = true) => {
    fakeStore.reset()
    fakeHitApi.setSuccess(success)
    resetRequestsCache()
  }

  it('dispatches success actions correctly', () => {
    reset()
    const result = actionsToCheck.reduce((
      promise: Promise<any>,
      action: RStore.Action<any>
    ) => {
      return promise.then(middleware(action))
    }, Promise.resolve()).then(() => {
      return {
        next: fakeStore.actionsProceededToNext,
        dispatch: fakeStore.actionsDispatched,
      }
    })

    const dispatchedActions = [
      apiSuccess(FETCH_HIT, 'fetchHit', fetchHit()),
      apiSuccess(GET_VISIT_INFO, 'getVisitInfo', getVisitInfo()),
      apiSuccess(FETCH_HITS_LIST, 'fetchHitsList', fetchHitsList()),
    ]

    return expect(result).resolves.toEqual({
      dispatch: dispatchedActions,
      next: actionsToCheck,
    })
  })

  it('dispatches error actions correctly', () => {
    reset(false)
    const result = actionsToCheck.reduce((
      promise: Promise<any>,
      action: RStore.Action<any>
    ) => {
      return promise.then(middleware(action).then(() => null, () => null))
    }, Promise.resolve()).then(() => {
      return {
        next: fakeStore.actionsProceededToNext,
        dispatch: fakeStore.actionsDispatched,
      }
    })

    const dispatchedActions = [
      apiError(FETCH_HIT, Error('fetchHit'), fetchHit()),
      apiError(GET_VISIT_INFO, Error('getVisitInfo'), getVisitInfo()),
      apiError(FETCH_HITS_LIST, Error('fetchHitsList'), fetchHitsList()),
    ]

    return expect(result).resolves.toEqual({
      dispatch: dispatchedActions,
      next: actionsToCheck,
    })
  })

  it('Caches requests without unwanted success dispatches', () => {
    reset()
    const initialDispatches = [
      getVisitInfo(),
      getVisitInfo(),
      getVisitInfo(),
    ]

    const result = Promise.all(
      initialDispatches.map((action: RStore.Action<any>) => middleware(action))
    )
    .then((() => middleware(getVisitInfo())))
    .then(() => ({
      next: fakeStore.actionsProceededToNext,
      dispatch: fakeStore.actionsDispatched,
    }))

    return expect(result).resolves.toEqual({
      dispatch: [apiSuccess(GET_VISIT_INFO, 'getVisitInfo', getVisitInfo())],
      next: [getVisitInfo()],
    })
  })

  it('Makes requests if previous iteration failed (for cached methods)', () => {
    reset(false)
    const calls = [
      getVisitInfo(),
      getVisitInfo(),
      getVisitInfo(),
    ]
    const dispathces = [
      apiError(GET_VISIT_INFO, Error('getVisitInfo'), getVisitInfo()),
      apiError(GET_VISIT_INFO, Error('getVisitInfo'), getVisitInfo()),
      apiError(GET_VISIT_INFO, Error('getVisitInfo'), getVisitInfo()),
    ]

    const result = calls.reduce(
      (promise: Promise<any>, action: RStore.Action<any>) =>
        promise.then(() => middleware(action)).then(() => null, () => null),
      Promise.resolve()
    ).then(() => ({
      next: fakeStore.actionsProceededToNext,
      dispatch: fakeStore.actionsDispatched,
    }))

    return expect(result).resolves.toEqual({
      dispatch: dispathces,
      next: calls,
    })
  })

  it('Requests non-cached methods', () => {
    reset(true)
    const calls = [
      setComment('comment1'),
      setFavorite(true),
      setComment('comment2'),
      setFavorite(false),
    ]
    const dispathces = [
      apiSuccess(SET_COMMENT, 'setComment', setComment('comment1')),
      apiSuccess(SET_FAVORITE, 'setFavorite', setFavorite(true)),
      apiSuccess(SET_COMMENT, 'setComment', setComment('comment2')),
      apiSuccess(SET_FAVORITE, 'setFavorite', setFavorite(false)),
    ]
    const result = calls.reduce(
      (promise: Promise<any>, action: RStore.Action<any>) =>
        promise.then(() => middleware(action)),
      Promise.resolve()
    ).then(() => ({
      next: fakeStore.actionsProceededToNext,
      dispatch: fakeStore.actionsDispatched,
    }))

    return expect(result).resolves.toEqual({
      dispatch: dispathces,
      next: calls,
    })
  })
})
