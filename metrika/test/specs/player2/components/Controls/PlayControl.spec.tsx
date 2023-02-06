import React from 'react'
import renderer from 'react-test-renderer'
import 'jest-styled-components'
import ActionsWrapper from '@test/utils/ActionsWrapper'
import timerActions, { play, pause, rewind } from '@player2/store/actions/timer'
import { PlayControl } from '@player2/components/Controls/PlayControl'
import MainThemeProvider from '@player2/components/Themes/MainThemeProvider'
import { mount } from 'enzyme'

describe('<PlayControl>', () => {
  const actionsWrapper = new ActionsWrapper(timerActions)
  const actionProps = actionsWrapper.getProxiedActions()
  const props = {
    playing: {
      playing: true,
      finished: false,
      ...actionProps,
    },
    stopped: {
      playing: false,
      finished: false,
      ...actionProps,
    },
    finished: {
      playing: false,
      finished: true,
      ...actionProps,
    },
  } as any
  it('Renders correctly', () => {
    let tree = renderer.create(<MainThemeProvider><PlayControl {...props.playing}/></MainThemeProvider>).toJSON()
    expect(tree).toMatchSnapshot()
    tree = renderer.create(<MainThemeProvider><PlayControl {...props.stopped}/></MainThemeProvider>).toJSON()
    expect(tree).toMatchSnapshot()
  })

  it('Calls play, pause, and rewind', () => {
    actionsWrapper.clear()
    let element = mount(<MainThemeProvider><PlayControl {...props.playing}/></MainThemeProvider>)
    element.find('button').simulate('click')

    element = mount(<MainThemeProvider><PlayControl {...props.stopped}/></MainThemeProvider>)
    element.find('button').simulate('click')

    element = mount(<MainThemeProvider><PlayControl {...props.finished}/></MainThemeProvider>)
    element.find('button').simulate('click')

    expect(actionsWrapper.getCalledActions()).toEqual([
      pause(true),
      play(true),
      rewind(0),
      play(true),
    ])
  })
})
