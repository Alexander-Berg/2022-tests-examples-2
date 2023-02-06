import 'jest-styled-components'

import React from 'react'
import renderer from 'react-test-renderer'
import { App } from '@player2/components/App'
import ActionsWrapper from '@test/utils/ActionsWrapper'
import timerActions from '@player2/store/actions/timer'
import hitsCacheActions from '@player2/store/actions/currentHit'
import apiActions from '@player2/store/actions/api'
import wait from '@test/utils/wait'

jest.mock('@player2/components/UI/Main', () => {
  return () => 'This is UI, and I am a princess!'
})

describe('<App>', () => {
  const actionsWrapper = new ActionsWrapper(
    {
      ...timerActions,
      ...hitsCacheActions,
      ...apiActions,
    },
    {
      fetchHitsList: {
        async: true,
        returns: [],
      },
      fetchHit: {
        async: true,
        returns: {},
      },
      rewind: {
        async: true,
      },
      getVisitInfo: {
        async: true,
        returns: {
          result: {
            tabChanges: [
              {
                stamp: 1,
                watchId: 1,
              },
              {
                stamp: 1,
                watchId: 2,
              },
              {
                stamp: 1,
                watchId: 3,
              },
            ],
          },
        },
      },
    }
  )
  const actionsProps = actionsWrapper.getProxiedActions()

  it('Renders loader', () => {
    let props: any = {
      config: {autoplay: true},
      currentHit: null,
      api: {
        hitsCache: {},
        hitsList: {data: {}},
        visitInfo: {data: {}},
        activityMap: {data: {}},
      },
      ...actionsProps,
    }
    let tree = renderer.create(<App {...props}/>).toJSON()
    expect(tree).toMatchSnapshot()

    props = {
      config: {autoplay: true},
      currentHit: null,
      api: {
        hitsCache: {},
        hitsList: {data: null, fetching: true},
        visitInfo: {data: {}},
      },
      ...actionsProps,
    }
    tree = renderer.create(<App {...props}/>).toJSON()
    expect(tree).toMatchSnapshot()

    props = {
      config: {autoplay: true},
      currentHit: null,
      api: {
        hitsCache: {},
        hitsList: {data: {}},
        visitInfo: {data: null, fetchign: true},
      },
      ...actionsProps,
    }

    tree = renderer.create(<App {...props}/>).toJSON()
    expect(tree).toMatchSnapshot()
  })

  it('Renders error', () => {
    let props: any = {
      config: {autoplay: true},
      currentHit: {},
      api: {
        hitsCache: {},
        hitsList: {data: null, error: new Error('shit happened!')},
        visitInfo: {data: null, fetching: true},
      },
      ...actionsProps,
    }
    let tree = renderer.create(<App {...props}/>).toJSON()
    expect(tree).toMatchSnapshot()
    props = {
      config: {autoplay: true},
      currentHit: {},
      api: {
        hitsCache: {},
        hitsList: {data: {}},
        visitInfo: {data: null, error: new Error('shit happened!')},
      },
      ...actionsProps,
    }
    tree = renderer.create(<App {...props}/>).toJSON()
    expect(tree).toMatchSnapshot()
  })

  it('Renders content', () => {
    let props: any = {
      config: {autoplay: true},
      currentHit: {},
      api: {
        hitsCache: {},
        hitsList: {data: []},
        visitInfo: {data: {}},
      },
      ...actionsProps,
    }
    let tree = renderer.create(<App {...props}/>).toJSON()
    expect(tree).toMatchSnapshot()
  })

  it('Calls all the necessary prefetch methods', async () => {
    actionsWrapper.clear()
    const props: any = {
      config: {autoplay: true},
      currentHit: {},
      api: {
        hitsCache: {},
        hitsList: {data: []},
        visitInfo: {data: {}},
      },
      ...actionsProps,
    }
    renderer.create(<App {...props}/>).toJSON()
    await wait()

    expect(actionsWrapper.getCalledActions()).toEqual([
      apiActions.getVisitInfo(),
      apiActions.fetchHitsList(),
      timerActions.rewind(0, true),
      apiActions.fetchHit(1),
      apiActions.fetchHit(2),
      apiActions.fetchHit(3),
    ])
  })
})
