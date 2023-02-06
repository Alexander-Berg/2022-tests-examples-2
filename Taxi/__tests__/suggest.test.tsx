import {renderHook} from '@testing-library/react-hooks'
import {ComponentType} from 'react'

import {createTestWrapper} from '../../../../tests'
import {actWait} from '../../../../tests/utils/act-wait'
import {useSuggest} from '../use-suggest'

interface WrapperProps {
  query: string
}

describe('hooks.Suggest', () => {
  it('Можно запросить адреса через useSuggest', async () => {
    const {result, waitFor, rerender} = renderHook(
      ({query}: WrapperProps) => {
        return useSuggest({
          query,
          point: {
            lon: 0,
            lat: 0,
          },
          lang: 'ru',
          debounceDelay: 0,
        })
      },
      {
        wrapper: createTestWrapper({}) as ComponentType<WrapperProps>,
        initialProps: {
          query: 'Садовническая 82',
        },
      },
    )

    const rerenderAndWaitForDebounce = async (props: WrapperProps) => {
      rerender(props)

      // ждем debounce внутри хука
      await actWait(0)
    }

    // 1
    expect(result.current.suggest.isLoading).toBe(true)

    await waitFor(() => result.current.suggest.isSuccess)

    // 2
    expect(result.current.suggest.data?.items.length).toBe(25)

    await rerenderAndWaitForDebounce({
      query: 'малые каменщики',
    })

    // 3
    expect(result.current.suggest.isLoading).toBe(true)

    await waitFor(() => result.current.suggest.isSuccess)

    // 4
    expect(result.current.suggest.data?.items.length).toBe(13)
    expect(result.current.searchCount).toBe(1)
    expect(result.current.isEmptyResult).toBe(false)

    await rerenderAndWaitForDebounce({
      query: '',
    })

    await waitFor(() => result.current.suggest.isSuccess)

    // 5
    expect(result.current.suggest.data?.items.length).toBe(25)
    expect(result.current.searchCount).toBe(1)
    expect(result.current.isEmptyResult).toBe(false)

    await rerenderAndWaitForDebounce({
      query: '123',
    })

    await waitFor(() => result.current.suggest.isSuccess)

    // 6
    expect(result.current.suggest.data?.items.length).toBe(0)
    expect(result.current.searchCount).toBe(2)
    expect(result.current.isEmptyResult).toBe(true)
  })
})
