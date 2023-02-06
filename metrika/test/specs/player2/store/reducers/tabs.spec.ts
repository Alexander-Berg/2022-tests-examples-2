import { processTabsChanges } from '@player2/store/actions/tabs'
import reducer from '@player2/store/reducers/tabs'

describe('Processes tabs cahnges', () => {
  it('Adds tabs', () => {
    const state = reducer(
      {tabs: {'3': 4, '4': 5}, activeTab: '3'},
      processTabsChanges([
        {
          type: 'close',
          watchId: 5,
          tabId: '4',
          stamp: 0,
        },
        {
          type: 'select',
          watchId: 1,
          tabId: '3',
          stamp: 0,
        },
        {
          type: 'select',
          watchId: 2,
          tabId: '2',
          stamp: 1,
        },
        {
          type: 'close',
          watchId: 1,
          tabId: '2',
          stamp: 2,
        },
        {
          type: 'select',
          watchId: 3,
          tabId: '1',
          stamp: 3,
        },
      ], true)
    )
    expect(state).toEqual({
      tabs: {
        '3': 1,
        '1': 3,
      },
      activeTab: '1',
    })
  })

  it('Adds tabs and resets', () => {
    const state = reducer(
      {tabs: {'3': 4}, activeTab: '3'},
      processTabsChanges([
        {
          type: 'select',
          watchId: 1,
          tabId: '1',
          stamp: 0,
        },
        {
          type: 'select',
          watchId: 2,
          tabId: '2',
          stamp: 1,
        },
        {
          type: 'close',
          watchId: 1,
          tabId: '2',
          stamp: 2,
        },
        {
          type: 'select',
          watchId: 3,
          tabId: '1',
          stamp: 3,
        },
      ], true)
    )
    expect(state).toEqual({
      tabs: {
        '1': 3,
      },
      activeTab: '1',
    })
  })
})