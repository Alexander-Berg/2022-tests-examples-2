import fakeBrowser from '@test/fakes/fakeBrowser'
import FakeIndexer from '@test/fakes/fakeIndexer'
import MouseMoveRenderer from '@player2/renderers/MouseMoveRenderer'
import IndexerContainer from '@player2/utils/IndexerContainer'

describe('MouseMoveRenderer', () => {
  const indexer = new FakeIndexer(window.document)
  const renderer = new MouseMoveRenderer(
    new IndexerContainer(
      indexer as any,
      window as any
    ),
    fakeBrowser as any,
    {} as any
  )

  it('moves mouse', () => {
    fakeBrowser.reset()
    renderer.handlePlayerRecord({
      group: 'event',
      meta: {x: 100, y: 100},
      type: 'mousemove',
      stamp: 10,
    } as any)
    expect(fakeBrowser.mousePosition).toEqual({x: 100, y: 100})

    renderer.handlePlayerRecord({
      group: 'event',
      meta: {x: 10, y: 10},
      type: 'mouseup',
      stamp: 10,
    } as any)
    expect(fakeBrowser.mousePosition).toEqual({x: 10, y: 10})

    renderer.handlePlayerRecord({
      group: 'event',
      meta: {x: 1, y: 1},
      type: 'mousedown',
      stamp: 10,
    } as any)
    expect(fakeBrowser.mousePosition).toEqual({x: 1, y: 1})
  })
})