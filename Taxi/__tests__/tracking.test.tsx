import {renderHook, act} from '@testing-library/react-hooks'

import {identifiers} from '@lavka/constants'
import {CONFIRM_MODAL_ID, ConfirmModalCloseResult, createTestStore} from '@lavka/store'

import {createTestWrapper} from '../../../../tests'
import {useCancelOrder} from '../use-cancel-order'
import {useTracking} from '../use-tracking'

const ORDER_ID = identifiers.orderSadovnicheskaya

describe.skip('hooks.Tracking', () => {
  it('Можно запросить заказ через useTracking', async () => {
    const {result, waitFor} = renderHook(() => useTracking({id: ORDER_ID}), {
      wrapper: createTestWrapper({}),
    })

    await waitFor(() => result.current.order.isSuccess)

    expect(result.current.order.data).toBeDefined()
  })

  it('Можно отменить заказ через useCancelOrder', async () => {
    const store = createTestStore()
    const {result, waitFor} = renderHook(
      () => ({
        tracking: useTracking({id: ORDER_ID}),
        cancelOrder: useCancelOrder({id: ORDER_ID}),
      }),
      {
        wrapper: createTestWrapper({store}),
      },
    )

    await waitFor(() => result.current.tracking.order.isSuccess)

    expect(result.current.tracking.order.data?.id).toBe(ORDER_ID)
    expect(result.current.tracking.order.data?.status).toBe('created')

    act(() => {
      result.current.cancelOrder.cancelOrder()
    })

    expect(store.modals.visibleModals).toContain(CONFIRM_MODAL_ID)

    store.modals.forceClose<ConfirmModalCloseResult>(CONFIRM_MODAL_ID, {isConfirm: true})

    await waitFor(() => result.current.cancelOrder.isSuccess)

    // TODO
    // expect(result.current.tracking.order.data?.status).toBe('closed')
  })
})
