import fakeBrowser from '@test/fakes/fakeBrowser'
import FakeIndexer from '@test/fakes/fakeIndexer'
import MouseClickRenderer, { MOUSE_CLICK_LENGTH_THREASHOLD } from '@player2/renderers/MouseClickRenderer'
import IndexerContainer from '@player2/utils/IndexerContainer'

describe('MouseClickRenderer', () => {
  const indexer = new FakeIndexer(window.document)
  const renderer = new MouseClickRenderer(
    new IndexerContainer(
      indexer as any,
      window as any
    ),
    fakeBrowser as any,
    {} as any
  )

  it('adds mouse click', () => {
    fakeBrowser.reset()
    renderer.handlePlayerRecord({group: 'events', type: 'mousedown', meta: {x: 10, y: 10}, stamp: 0} as any)
    expect(fakeBrowser.mouseClicked).toBeTruthy()
  })

  it('releases mouse click', () => {
    fakeBrowser.reset()
    renderer.reset()
    renderer.handlePlayerRecord({group: 'events', type: 'mousedown', meta: {x: 10, y: 10}, stamp: 0} as any)
    renderer.handlePlayerRecord({group: 'events', type: 'mouseup', stamp: 1} as any)
    expect(fakeBrowser.mouseClicked).toBeFalsy()
  })

  it('moves click', () => {
    fakeBrowser.reset()
    renderer.reset()
    renderer.handlePlayerRecord({group: 'events', type: 'mousedown', meta: {x: 10, y: 10}, stamp: 0} as any)
    renderer.handlePlayerRecord({group: 'events', type: 'mousemove', meta: {x: 20, y: 20}, stamp: 1} as any)
    expect(fakeBrowser.mouseClicked).toBeTruthy()
    expect(fakeBrowser.mousePosition).toEqual({x: 20, y: 20})
  })

  it('removes click after it\'s expiration', () => {
    fakeBrowser.reset()
    renderer.reset()
    renderer.handlePlayerRecord({group: 'events', type: 'mousedown', meta: {x: 10, y: 10}, stamp: 0} as any)
    renderer.onTime(MOUSE_CLICK_LENGTH_THREASHOLD + 1)
    expect(fakeBrowser.mouseClicked).toBeFalsy()
  })

  it('resets click', () => {
    fakeBrowser.reset()
    renderer.reset()
    renderer.handlePlayerRecord({group: 'events', type: 'mousedown', meta: {x: 10, y: 10}, stamp: 0} as any)
    renderer.reset()
    expect(fakeBrowser.mouseClicked).toBeFalsy()
  })
})