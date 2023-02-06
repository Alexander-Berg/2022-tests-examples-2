import {useEffect} from 'react'

import {ConfirmModalCloseResult, ConfirmModalOpenProps, ModalComponentProps} from '../../src/types/modals'

interface TestConfirmModalProps extends ModalComponentProps<ConfirmModalCloseResult>, ConfirmModalOpenProps {}

export const TestConfirmModal = ({close, markAsClosed, forceClose}: TestConfirmModalProps) => {
  useEffect(() => {
    if (markAsClosed) {
      forceClose()
    }
  }, [forceClose, markAsClosed])

  const handleConfirm = () => {
    close({isConfirm: true})
  }

  const handleCancel = () => {
    close({isConfirm: false})
  }

  return (
    <div role="dialog">
      <h1>Confirm</h1>
      <button type="button" onClick={handleConfirm}>
        confirm
      </button>
      <button type="button" onClick={handleCancel}>
        cancel
      </button>
    </div>
  )
}
