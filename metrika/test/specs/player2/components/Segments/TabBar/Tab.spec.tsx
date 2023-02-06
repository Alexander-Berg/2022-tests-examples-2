import React from 'react'
import renderer from 'react-test-renderer'
import { Tab } from '@player2/components/UI/TabBar/Tab'
import 'jest-styled-components'

describe('<Tab>', () => {
  it('Renders correctly', () => {
    let tree = renderer
      .create(<Tab label="Name" active={false} />)
      .toJSON()
    expect(tree).toMatchSnapshot()
    tree = renderer
      .create(<Tab label="Name" active={true} />)
      .toJSON()
    expect(tree).toMatchSnapshot()
  })
})
