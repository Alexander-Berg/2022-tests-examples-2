import browser from '@test/fakes/fakeBrowser'
import IndexerContainer from '@player2/utils/IndexerContainer'
import DevicePanelsRenderer from '@player2/renderers/DevicePanelsRenderer'

describe('DevicePanelsRenderer', () => {

  it('Opens panels in ios', async () => {
    expect.assertions(5)
    browser.reset()
    const renderer = new DevicePanelsRenderer(
      new IndexerContainer({} as any, {} as any),
      browser as any,
      {
        width: 100,
        height: 100,
        osType: 'ios',
      } as any
    )

    await renderer.handlePlayerRecord({
      group: 'event',
      type: 'focus',
    } as any)
    expect(browser.panels).toEqual({topPanel: false, bottomPanel: true})

    await renderer.handlePlayerRecord({
      group: 'event',
      type: 'blur',
    } as any)
    expect(browser.panels).toEqual({topPanel: false, bottomPanel: false})

    // Too small resize to actually matter
    await renderer.handlePlayerRecord({
      group: 'event',
      type: 'resize',
      meta: {height: 99, width: 100},
    } as any)
    expect(browser.panels).toEqual({topPanel: false, bottomPanel: false})

    await renderer.handlePlayerRecord({
      group: 'event',
      type: 'resize',
      meta: {height: 60, width: 100},
    } as any)
    expect(browser.panels).toEqual({topPanel: true, bottomPanel: false})

    await renderer.handlePlayerRecord({
      group: 'event',
      type: 'resize',
      meta: {height: 100, width: 100},
    } as any)
    expect(browser.panels).toEqual({topPanel: false, bottomPanel: false})
  })

  it('Opens panels in android', async () => {
    expect.assertions(4)
    browser.reset()
    const renderer = new DevicePanelsRenderer(
      new IndexerContainer({} as any, {} as any),
      browser as any,
      {
        width: 100,
        height: 100,
        osType: 'android',
      } as any
    )

    // Too small resize to actually matter
    await renderer.handlePlayerRecord({
      group: 'event',
      type: 'resize',
      meta: {height: 90, width: 100},
    } as any)
    expect(browser.panels).toEqual({topPanel: false, bottomPanel: false})

    await renderer.handlePlayerRecord({
      group: 'event',
      type: 'resize',
      meta: {height: 70, width: 100},
    } as any)
    expect(browser.panels).toEqual({topPanel: true, bottomPanel: false})

    await renderer.handlePlayerRecord({
      group: 'event',
      type: 'resize',
      meta: {height: 59, width: 100},
    } as any)
    expect(browser.panels).toEqual({topPanel: true, bottomPanel: true})

    await renderer.handlePlayerRecord({
      group: 'event',
      type: 'resize',
      meta: {height: 100, width: 100},
    } as any)
    expect(browser.panels).toEqual({topPanel: false, bottomPanel: false})

  })
})