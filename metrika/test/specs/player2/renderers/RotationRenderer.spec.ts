import browser from '@test/fakes/fakeBrowser'
import FakeIndexer from '@test/fakes/fakeIndexer'
import IndexerContainer from '@player2/utils/IndexerContainer'
import RotationRenderer from '@player2/renderers/RotationRenderer'

describe('RotationRenderer', () => {
  it('Calls browser setRotation method', async () => {
    browser.reset()
    const indexer = new FakeIndexer(window.document)
    const renderer = new RotationRenderer(
      new IndexerContainer(
        indexer as any,
        window as any
      ),
      browser as any,
      {} as any
    )

    await renderer.handlePlayerRecord({
      group: 'events',
      type: 'deviceRotation',
      frameId: 1,
      meta: {
        orientation: 90,
      },
    } as any)
    expect(browser.orientation).toEqual(90)
  })
})