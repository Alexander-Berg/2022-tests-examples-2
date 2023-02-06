import React from 'react'
import {fireEvent, render} from '@testing-library/react'
import Section from './Section'
import {MetrikaStub, EnvContextTest} from 'shared/test-utils'

describe('Section', () => {
  test('Должны отправляться события в метрику при разворачивании/сворачивании', () => {
    const sectionName = 'QR-меню'
    const metrika = new MetrikaStub()
    metrika.reachGoal = jest.fn()

    const {getByRole} = render(
      <EnvContextTest.Provider value={{metrika}}>
        <Section title={sectionName} titleJsx={<span>Custom name</span>} metrikaParams={{place_id: 1}}>
          <p>Section content</p>
        </Section>
      </EnvContextTest.Provider>
    )

    const clickableDiv = getByRole('button')
    fireEvent.click(clickableDiv)

    expect(metrika.reachGoal).toBeCalledWith('ui_section_expand', {name: sectionName, expanded: false, place_id: 1})

    fireEvent.click(clickableDiv)
    expect(metrika.reachGoal).toBeCalledWith('ui_section_expand', {name: sectionName, expanded: true, place_id: 1})
  })
})
