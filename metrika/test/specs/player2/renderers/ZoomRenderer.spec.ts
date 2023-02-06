import browser from '@test/fakes/fakeBrowser'
import FakeIndexer from '@test/fakes/fakeIndexer'
import IndexerContainer from '@player2/utils/IndexerContainer'
import ZoomRenderer from '@player2/renderers/ZoomRenderer'

describe('ZoomRenderer', () => {
  it('Handles zoom event', async () => {
    browser.reset()
    const indexer = new FakeIndexer(window.document)

    const renderer = new ZoomRenderer(
      new IndexerContainer(
        indexer as any,
        window as any
      ),
      browser as any,
      {} as any
    )
    await renderer.handlePlayerRecord({
      group: 'events',
      type: 'zoom',
      meta: {
        zoomLevel: 2,
      },
    } as any)
    expect(browser.zoomLevel).toEqual(2)
  })
})