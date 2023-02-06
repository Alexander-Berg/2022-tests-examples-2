import {render, fireEvent, screen} from '@testing-library/react'

import {TestModal} from '..'
import {ModalsInjector, useRegisterModal, StoreProvider} from '../..'
import {createTestStore} from '../utils/create-test-store'

const MODAL_ID = 'MODAL_ID'

const TestApp = () => {
  useRegisterModal({
    id: MODAL_ID,
    type: 'modal',
    ModalComponent: TestModal,
    props: {
      closeResult: {data: '2'},
    },
  })

  return (
    <>
      <ModalsInjector />
      <div role="main">app content</div>
    </>
  )
}

describe('ModalsInjector', () => {
  it('Регистрация модалки, открытие, закрытие через методы модели', async () => {
    const store = createTestStore()

    render(
      <StoreProvider store={store}>
        <TestApp />
      </StoreProvider>,
    )

    expect(screen.getByRole('main')).toBeInTheDocument()
    expect(screen.queryByRole('dialog')).toBeNull()

    const modalPromise = store.modals.open(MODAL_ID)

    expect(screen.getByRole('dialog')).toBeInTheDocument()

    const closeResult = {
      data: '1',
    }
    store.modals.close(MODAL_ID, closeResult)

    const result = await modalPromise

    expect(result).toEqual(closeResult)
    expect(screen.queryByRole('dialog')).toBeNull()
  })

  it('Регистрация модалки, открытие, закрытие через кнопку в модалке', async () => {
    const store = createTestStore()

    render(
      <StoreProvider store={store}>
        <TestApp />
      </StoreProvider>,
    )

    expect(screen.getByRole('main')).toBeInTheDocument()
    expect(screen.queryByRole('dialog')).toBeNull()

    const modalPromise = store.modals.open(MODAL_ID)

    expect(screen.getByRole('dialog')).toBeInTheDocument()

    const closeButton = screen.getByText('close')

    fireEvent.click(closeButton)

    const result = await modalPromise

    expect(result).toMatchObject({data: '2'})
    expect(screen.queryByRole('dialog')).toBeNull()
  })
})
