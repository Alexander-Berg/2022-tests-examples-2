import React from 'react'
import renderer from 'react-test-renderer'
import 'jest-styled-components'
import ActionsWrapper from '@test/utils/ActionsWrapper'
import { PlaybackSpeedControl } from '@player2/components/Controls/PlaybackSpeedControl'
import MainThemeProvider from '@player2/components/Themes/MainThemeProvider'
import { setSpeed } from '@player2/store/actions/timer'
import { DEFAULT_PLAY_SPEED } from '@player2/store/reducers/timer'
import { mount } from 'enzyme'

describe('<PlaybackSpeedControl>', () => {
  const actionsWrapper = new ActionsWrapper({
    setSpeed,
  })
  const actionsProps = actionsWrapper.getProxiedActions()
  const props = {
    x1: {
      speed: DEFAULT_PLAY_SPEED,
      ...actionsProps,
    },
    x2: {
      speed: DEFAULT_PLAY_SPEED * 2,
      ...actionsProps,
    },
    x3: {
      speed: DEFAULT_PLAY_SPEED * 3,
      ...actionsProps,
    },
    x4: {
      speed: DEFAULT_PLAY_SPEED * 4,
      ...actionsProps,
    },
  } as any
  it ('renders correctly', () => {
    let tree = renderer.create(<MainThemeProvider><PlaybackSpeedControl {...props.x1}/></MainThemeProvider>).toJSON()
    expect(tree).toMatchSnapshot()
    tree = renderer.create(<MainThemeProvider><PlaybackSpeedControl {...props.x2}/></MainThemeProvider>).toJSON()
    expect(tree).toMatchSnapshot()
    tree = renderer.create(<MainThemeProvider><PlaybackSpeedControl {...props.x3}/></MainThemeProvider>).toJSON()
    expect(tree).toMatchSnapshot()
    tree = renderer.create(<MainThemeProvider><PlaybackSpeedControl {...props.x4}/></MainThemeProvider>).toJSON()
    expect(tree).toMatchSnapshot()
  })

  it  ('calls actions correctly', () => {
    actionsWrapper.clear()
    const element = mount(<MainThemeProvider><PlaybackSpeedControl {...props.x1}/></MainThemeProvider>)
    element.find('button').simulate('click')
    element.setProps({children: <PlaybackSpeedControl {...props.x2}/>})
    element.find('button').simulate('click')
    element.setProps({children: <PlaybackSpeedControl {...props.x3}/>})
    element.find('button').simulate('click')
    element.setProps({children: <PlaybackSpeedControl {...props.x4}/>})
    element.find('button').simulate('click')

    expect(actionsWrapper.getCalledActions()).toEqual([
      setSpeed(DEFAULT_PLAY_SPEED * 2),
      setSpeed(DEFAULT_PLAY_SPEED * 3),
      setSpeed(DEFAULT_PLAY_SPEED * 4),
      setSpeed(DEFAULT_PLAY_SPEED),
    ])
  })
})
