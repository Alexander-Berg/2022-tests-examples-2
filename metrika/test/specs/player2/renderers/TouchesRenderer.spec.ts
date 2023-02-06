import fakeBrowser from '@test/fakes/fakeBrowser'
import FakeIndexer from '@test/fakes/fakeIndexer'
import TouchesRenderer, { TOUCH_LENGTH_THREASHOLD } from '@player2/renderers/TouchesRenderer'
import IndexerContainer from '@player2/utils/IndexerContainer'

describe('TouchesRenderer', () => {
  const indexer = new FakeIndexer(window.document)
  const renderer = new TouchesRenderer(
    new IndexerContainer(
      indexer as any,
      window as any
    ),
    fakeBrowser as any,
    {} as any
  )

  it('adds touch', () => {
    fakeBrowser.reset()
    renderer.reset()
    renderer.handlePlayerRecord({
      group: 'events',
      type: 'touchstart',
      meta: {
        touches: [
          {id: 'a', x: 10, y: 10},
          {id: 'b', x: 20, y: 20},
        ],
      },
      stamp: 0,
    } as any)

    expect(fakeBrowser.getTouches()).toEqual([
      {id: 'a', x: 10, y: 10},
      {id: 'b', x: 20, y: 20},
    ])
  })

  it('removes touch', () => {
    fakeBrowser.reset()
    renderer.reset()
    renderer.handlePlayerRecord({
      group: 'events',
      type: 'touchstart',
      meta: {
        touches: [
          {id: 'a', x: 10, y: 10},
          {id: 'b', x: 20, y: 20},
        ],
      },
      stamp: 0,
    } as any)
    renderer.handlePlayerRecord({
      group: 'events',
      type: 'touchend',
      meta: {
        touches: [
          {id: 'a'},
        ],
      },
      stamp: 1,
    } as any)

    expect(fakeBrowser.getTouches()).toEqual([
      {id: 'b', x: 20, y: 20},
    ])
  })

  it('moves touch', () => {
    fakeBrowser.reset()
    renderer.reset()
    renderer.handlePlayerRecord({
      group: 'events',
      type: 'touchstart',
      meta: {
        touches: [
          {id: 'a', x: 10, y: 10},
          {id: 'b', x: 20, y: 20},
        ],
      },
      stamp: 0,
    } as any)
    renderer.handlePlayerRecord({
      group: 'events',
      type: 'touchmove',
      meta: {
        touches: [
          {id: 'a', x: 20, y: 20},
          {id: 'b', x: 20, y: 20},
        ],
      },
      stamp: 1,
    } as any)

    expect(fakeBrowser.getTouches()).toEqual([
      {id: 'a', x: 20, y: 20},
      {id: 'b', x: 20, y: 20},
    ])
  })

  it('removes touch after it\'s expiration', () => {
    fakeBrowser.reset()
    renderer.reset()
    renderer.handlePlayerRecord({
      group: 'events',
      type: 'touchstart',
      meta: {
        touches: [
          {id: 'a', x: 10, y: 10},
          {id: 'b', x: 20, y: 20},
        ],
      },
      stamp: 0,
    } as any)
    renderer.handlePlayerRecord({
      group: 'events',
      type: 'touchmove',
      meta: {
        touches: [
          {id: 'a', x: 20, y: 20},
        ],
      },
      stamp: 100,
    } as any)
    renderer.onTime(TOUCH_LENGTH_THREASHOLD + 1)

    expect(fakeBrowser.getTouches()).toEqual([
      {id: 'a', x: 20, y: 20},
    ])
  })

  it('resets touches', () => {
    fakeBrowser.reset()
    renderer.reset()
    renderer.handlePlayerRecord({
      group: 'events',
      type: 'touchstart',
      meta: {
        touches: [
          {id: 'a', x: 10, y: 10},
          {id: 'b', x: 20, y: 20},
        ],
      },
      stamp: 0,
    } as any)
    renderer.reset()

    expect(fakeBrowser.getTouches()).toEqual([])
  })
})