import React from 'react'
import renderer from 'react-test-renderer'
import { TabBar } from '@player2/components/UI/TabBar/index'
import 'jest-styled-components'

describe('<TabBar>', () => {
  it('Renders correctly (shows with 2 or more tabs)', () => {
    let props: any = {
      tabs: [],
    }
    let tree = renderer
      .create(<TabBar {...props}/>)
      .toJSON()
    expect(tree).toMatchSnapshot()
    props = {
      tabs: [
        {
          tabId: '1',
          active: true,
          title: 'title1',
        },
      ],
    }
    tree = renderer
      .create(<TabBar {...props}/>)
      .toJSON()
    expect(tree).toMatchSnapshot()
    props = {
      tabs: [
        {
          tabId: '1',
          title: 'title1',
          active: true,
        },
        {
          tabId: '2',
          title: 'title2',
          active: false,
        },
      ],
    }
    tree = renderer
      .create(<TabBar {...props}/>)
      .toJSON()
    expect(tree).toMatchSnapshot()
  })
})
