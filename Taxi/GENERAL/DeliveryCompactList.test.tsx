import { render, screen } from '@testing-library/react'

import { DeliveryCompactList } from './DeliveryCompactList'

describe('render delivery compact list', () => {
  test('Should render correct surge text after first render', () => {
    render(<DeliveryCompactList items={[{ title: 'title 1', description: 'description 1', isSurge: true }]} />)

    expect(screen.getByText('title 1')).toBeTruthy()
    expect(screen.getByText('description 1')).toBeTruthy()
  })

  test('Should render correct not surge text after first render', () => {
    render(<DeliveryCompactList items={[{ title: 'title 2', description: 'description 2' }]} />)

    expect(screen.getByText('title 2')).toBeTruthy()
    expect(screen.getByText('description 2')).toBeTruthy()
  })

  test('Should render separator between items if passed more than 1', () => {
    render(
      <DeliveryCompactList
        items={[
          { title: 'title 1', description: 'description 1' },
          { title: 'title 2', description: 'description 2' },
        ]}
      />,
    )

    expect(screen.getByRole('separator')).toBeTruthy()
  })
})
