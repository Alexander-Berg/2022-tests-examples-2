import browser from '@test/fakes/fakeBrowser'
import FakeIndexer from '@test/fakes/fakeIndexer'
import IndexerContainer from '@player2/utils/IndexerContainer'
import InputChangesRenderer from '@player2/renderers/InputChangesRenderer'

describe('InputChangesRendrer', () => {
  const indexer = new FakeIndexer(window.document)
  const input = window.document.createElement('input')
  const checkbox = window.document.createElement('input')
  input.setAttribute('type', 'text')
  checkbox.setAttribute('type', 'checkbox')

  indexer.add(1, input)
  indexer.add(2, checkbox)
  const renderer = new InputChangesRenderer(
    new IndexerContainer(
      indexer as any,
      window as any
    ),
    browser as any,
    {} as any
  )

  it('Changes input value', async () => {
    await renderer.handlePlayerRecord({
      group: 'events',
      type: 'change',
      frameId: 0,
      target: 1,
      meta: {
        value: 'Some text!',
      },
    } as any)
    expect(input.value).toEqual('Some text!')
  })

  it('Checkes some checkbox', async () => {
    await renderer.handlePlayerRecord({
      group: 'events',
      type: 'change',
      frameId: 0,
      target: 2,
      meta: {
        checked: true,
      },
    } as any)
    expect(checkbox.checked).toEqual(true)
  })
})