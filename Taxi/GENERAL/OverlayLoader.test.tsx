import { render, screen } from '@testing-library/react'

import { OverlayLoader } from './OverlayLoader'

describe('render overlay loader', () => {
  test('Should render correct content according for isLoading true', () => {
    render(
      <OverlayLoader isLoading>
        <div>Hello</div>
      </OverlayLoader>,
    )

    expect(screen.queryByText('Hello')).toBeTruthy()
  })

  test('Should render correct content according for isLoading false', () => {
    render(
      <OverlayLoader>
        <div>Hello</div>
      </OverlayLoader>,
    )

    expect(screen.queryByText('Hello')).toBeTruthy()
  })
})
