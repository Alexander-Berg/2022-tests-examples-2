import browser from '@test/fakes/fakeBrowser'
import FakeIndexer from '@test/fakes/fakeIndexer'
import IndexerContainer from '@player2/utils/IndexerContainer'
import ScrollRenderer from '@player2/renderers/ScrollRenderer'

describe('FocusRenderer', () => {
  const indexer = new FakeIndexer(window.document)

  it('Scrolls window', async () => {
    const fakeWindow = {
      x: 0,
      y: 0,
      window: true,
      document: {body: {}},
      scrollTo (x: number, y: number) {
        this.x = x
        this.y = y
      },
    }
    const indexerContainer = new IndexerContainer(indexer as any, {contentWindow: fakeWindow} as any)
    const renderer = new ScrollRenderer(
      indexerContainer,
      browser as any,
      {} as any
    )
    await renderer.handlePlayerRecord({
      group: 'events',
      type: 'scroll',
      frameId: 0,
      target: -1,
      meta: {
        x: 200,
        y: 100,
      },
    } as any)

    expect({x: fakeWindow.x, y: fakeWindow.y}).toEqual({x: 200, y: 100})
  })

  it('Scrolls elements', async () => {
    const indexerContainer = new IndexerContainer(indexer as any, {} as any)
    const fakeElement = {
      scrollTop: 0,
      scrollLeft: 0,
    }
    indexer.add(1, fakeElement as any)
    const renderer = new ScrollRenderer(
      indexerContainer,
      browser as any,
      {} as any
    )
    await renderer.handlePlayerRecord({
      group: 'events',
      type: 'scroll',
      frameId: 0,
      target: 1,
      meta: {
        x: 200,
        y: 100,
      },
    } as any)
    expect({x: fakeElement.scrollLeft, y: fakeElement.scrollTop}).toEqual({x: 200, y: 100})
  })
})