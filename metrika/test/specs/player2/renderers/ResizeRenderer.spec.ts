import browser from '@test/fakes/fakeBrowser'
import IndexerContainer from '@player2/utils/IndexerContainer'
import ResizeRenderer from '@player2/renderers/ResizeRenderer'

describe('ResizeRenderer', () => {
  it('Sets browser viewport', async () => {
    browser.reset()
    const renderer = new ResizeRenderer(
      new IndexerContainer({} as any, {} as any),
      browser as any,
      {} as any
    )

    await renderer.handlePlayerRecord({
      group: 'events',
      type: 'resize',
      meta: {
        width: 100,
        height: 100,
      },
    } as any)

    expect(browser.viewport).toEqual({
      width: 100,
      height: 100,
    })
  })
})
