import browser from '@test/fakes/fakeBrowser'
import FakeIndexer from '@test/fakes/fakeIndexer'
import IndexerContainer from '@player2/utils/IndexerContainer'
import FocusRenderer from '@player2/renderers/FocusRenderer'

describe('FocusRenderer', () => {
  const indexer = new FakeIndexer(window.document)
  const input = window.document.createElement('input')
  input.setAttribute('type', 'number')
  window.document.body.appendChild(input)
  indexer.add(
    1,
    input
  )

  const renderer = new FocusRenderer(
    new IndexerContainer(
      indexer as any,
      window as any
    ),
    browser as any,
    {} as any
  )

  it('Focuses on element', async () => {
    input.blur()
    await renderer.handlePlayerRecord({
      group: 'events',
      type: 'focus',
      target: 1,
      frameId: 0,
    } as any)
    expect(window.document.activeElement === input).toEqual(true)
  })

  it('Blures element', async () => {
    input.focus()
    await renderer.handlePlayerRecord({
      group: 'events',
      type: 'blur',
      target: 1,
      frameId: 0,
    } as any)
    expect(window.document.activeElement === input).toEqual(false)
  })
})