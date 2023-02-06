import {useEffect} from 'react'

import {ModalComponentProps} from '../../src/types/modals'

interface TestModalProps
  extends ModalComponentProps<{
    data: string
  }> {
  closeResult: {
    data: string
  }
}

export const TestModal = ({close, markAsClosed, forceClose, closeResult}: TestModalProps) => {
  useEffect(() => {
    if (markAsClosed) {
      forceClose()
    }
  }, [forceClose, markAsClosed])

  const handleClose = () => {
    close(closeResult)
  }

  return (
    <div role="dialog">
      <h1>Modal</h1>
      <button type="button" onClick={handleClose}>
        close
      </button>
    </div>
  )
}
