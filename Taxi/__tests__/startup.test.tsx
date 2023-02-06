import {renderHook} from '@testing-library/react-hooks'

import {createTestQueryClient, createTestWrapper} from '../../../../tests'
import {useStartup} from '../startup'
import {setUserAddress} from '../user-address'

describe('hooks.useStartup', () => {
  it('Можно запросить useStartup', async () => {
    const queryClient = createTestQueryClient()
    const {result, waitFor, rerender} = renderHook(
      () => {
        return useStartup()
      },
      {
        wrapper: createTestWrapper({queryClient}),
      },
    )

    expect(result.current.isSuccess).toBe(false)

    setUserAddress(queryClient, {
      lat: 1,
      lon: 2,
    })

    rerender({})

    await waitFor(() => result.current.isSuccess)

    expect(result.current.isSuccess).toBe(true)
  })
})
