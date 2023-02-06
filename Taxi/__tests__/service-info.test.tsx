import {renderHook} from '@testing-library/react-hooks'

import {createTestQueryClient, createTestWrapper} from '../../../../tests'
import {useServiceInfo} from '../service-info'

describe('hooks.useServiceInfo', () => {
  it('Можно запросить useServiceInfo', async () => {
    const queryClient = createTestQueryClient()
    const {result, waitFor, rerender} = renderHook(
      () => {
        return useServiceInfo({position: {location: [1, 2]}})
      },
      {
        wrapper: createTestWrapper({queryClient}),
      },
    )

    expect(result.current.isSuccess).toBe(false)

    rerender({})

    await waitFor(() => result.current.isSuccess)

    expect(result.current.isSuccess).toBe(true)
  })
})
