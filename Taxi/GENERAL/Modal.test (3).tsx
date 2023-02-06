import { fireEvent, render, screen } from '@testing-library/react'
import type { FC } from 'react'
import { RecoilRoot } from 'recoil'

import type { I18nApi } from '@lavka/i18n'
import { I18nProvider } from '@lavka/i18n'

import type { ModalProps } from './Modal'
import { Modal } from './Modal'

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const i18n = { common: () => 'close' } as any
const i18nApi: I18nApi = {
  i18n,
  i18nRaw: i18n,
  i18nCheck: i18n,
  lang: () => 'ru',
}

const TestModal: FC<ModalProps> = (props) => (
  <RecoilRoot>
    <I18nProvider api={i18nApi}>
      <Modal {...props} />
    </I18nProvider>
  </RecoilRoot>
)

const CloseWrapper: FC = ({ children }) => <div data-testid="close-elem">{children}</div>

describe('render modal', () => {
  test('Should render null passed element for closed modal', () => {
    render(
      <TestModal>
        <div data-testid="elem">Hello</div>
      </TestModal>,
    )

    expect(screen.queryByRole('button', { name: 'close' })).toBeFalsy()
    expect(screen.queryByTestId('elem')).toBeNull()
  })
  test('Should render passed node inside opened modal', () => {
    render(
      <TestModal isOpen>
        <div data-testid="elem">Hello</div>
      </TestModal>,
    )

    expect(screen.getByText('Hello')).toBeTruthy()
    expect(screen.getByTestId('elem')).toBeTruthy()
  })

  test('Should render modal from closed to opened', () => {
    const { rerender } = render(
      <TestModal>
        <div>Hello</div>
      </TestModal>,
    )

    rerender(
      <TestModal isOpen>
        <div>Hello</div>
      </TestModal>,
    )

    expect(screen.getByText('Hello')).toBeTruthy()
  })

  test('Should render exit button as children of render icon method', () => {
    const handleClose = jest.fn()

    render(
      <TestModal isOpen closeWrapper={CloseWrapper} onClose={handleClose}>
        <div>Hello</div>
      </TestModal>,
    )

    const buttonWrapper = screen.getAllByTestId('close-elem')[1]
    expect(buttonWrapper.querySelector('svg')).toBeTruthy()
  })

  test('Should render null instead of close button if isCloseButtonHidden flag is on', () => {
    render(
      <TestModal isCloseButtonHidden>
        <div>Hello</div>
      </TestModal>,
    )

    const closeButton = screen.queryByLabelText('close')
    expect(closeButton).toBeNull()
  })

  test('Should call close handler if click to close modal', () => {
    const handleClose = jest.fn()

    render(
      <TestModal onClose={handleClose} isOpen>
        <div>Hello</div>
      </TestModal>,
    )

    const closeButton = screen.getAllByLabelText('close')[0]

    fireEvent.click(closeButton)

    expect(handleClose).toHaveBeenCalledTimes(1)
  })
})
