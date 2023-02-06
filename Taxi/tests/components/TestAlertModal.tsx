import {useEffect} from 'react'

import {AlertModalOpenProps, ModalComponentProps} from '../../src/types/modals'

interface TestAlertModalProps extends ModalComponentProps, AlertModalOpenProps {}

export const TestAlertModal = ({close, markAsClosed, forceClose}: TestAlertModalProps) => {
  useEffect(() => {
    if (markAsClosed) {
      forceClose()
    }
  }, [forceClose, markAsClosed])

  const handleConfirm = () => {
    close()
  }

  return (
    <div role="dialog">
      <h1>Alert</h1>
      <button type="button" onClick={handleConfirm}>
        Ok
      </button>
    </div>
  )
}
