import { fireEvent, isInaccessible, render, screen } from '@testing-library/react'

import type { I18nApi } from '@lavka/i18n'
import { I18nProvider } from '@lavka/i18n'

import type { SuggestProps } from './Suggest'
import { Suggest } from './Suggest'
import type { Item } from './types'

jest.mock('uuid', () => {
  let gen = 1
  return {
    v4: () => 'uuidv4-' + gen++,
  }
})

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const i18n = { search: (key: string) => key } as any
const i18nApi: I18nApi = {
  i18n,
  i18nRaw: i18n,
  i18nCheck: i18n,
  lang: () => 'ru',
}

const initValue = 'test value'
const items = Array.from(Array(3).keys()).map((_, index) => ({ label: 'label' + index }))

function TestSuggest<TItem extends Item>(props: SuggestProps<TItem>) {
  return (
    <I18nProvider api={i18nApi}>
      <Suggest className="className" placeholder="search" value={initValue} {...props} />
    </I18nProvider>
  )
}

function checkAttributes(element: HTMLElement, attributes: Record<string, string | boolean>) {
  Object.entries(attributes).forEach(([name, value]) => {
    const attributeValue = element.getAttribute(name)
    expect(typeof value === 'boolean' ? !!attributeValue == value : attributeValue === value).toBeTruthy()
  })
}

describe('Suggest', () => {
  test('Начальное состояние без items', () => {
    render(<TestSuggest items={[]} />)

    const input = screen.getByDisplayValue(initValue)
    expect(input).toBeTruthy()
    checkAttributes(input, {
      role: 'combobox',
      'aria-haspopup': 'listbox',
      'aria-expanded': 'false',
      'aria-autocomplete': 'list',
      'aria-controls': true,
      'aria-label': 'search',
      placeholder: 'search',
    })

    const clearButton = document.querySelector('button[aria-label="clear"]')
    expect(clearButton).toBeTruthy()
    const clearSvg = clearButton?.querySelector('svg')
    expect(clearSvg ? isInaccessible(clearSvg) : true).toBeTruthy()
  })

  test('Компонент без пропсов', async () => {
    render(<TestSuggest placeholder={undefined} value={undefined} />)

    const container = await screen.findByRole('combobox')
    expect(container.querySelector('[role="listbox"]')).toBeFalsy()
  })

  test('Изменение инпута', () => {
    const handleChangeValue = jest.fn()
    const initValue = 'init value'
    render(<TestSuggest onChangeValue={handleChangeValue} value={initValue} />)

    const input = screen.getByDisplayValue(initValue)
    const value = 'new value'
    fireEvent.change(input, { target: { value } })
    expect(handleChangeValue).toHaveBeenCalledWith(value)
    expect(screen.getByDisplayValue(value)).toBeTruthy()
  })

  test('Проверка renderItem пропса', () => {
    render(
      <TestSuggest
        items={items}
        renderItem={({ label }) => (
          <div>
            <span>{label}</span>
            <span>{label + '-secondary'}</span>
          </div>
        )}
      />,
    )

    const input = screen.getByDisplayValue(initValue)
    fireEvent.focus(input)
    expect(screen.getByRole('listbox')).toMatchSnapshot()
  })

  test('Выбор элемента из саджеста', () => {
    const handleSelectValue = jest.fn()
    render(<TestSuggest items={items} onSelectItem={handleSelectValue} />)

    const input = screen.getByDisplayValue(initValue)
    fireEvent.focus(input)
    expect(screen.queryByRole('listbox')).toBeTruthy()
    const item1 = screen.getByText('label1')

    expect(item1.closest('[aria-selected="true"]')).toBeFalsy()
    fireEvent.mouseEnter(item1)
    expect(item1.closest('[aria-selected="true"]')).toBeTruthy()

    fireEvent.click(item1)
    expect(handleSelectValue).toHaveBeenCalledWith(items[1])
    expect(screen.queryByRole('listbox')).toBeFalsy()
    expect(screen.getByDisplayValue('label1')).toBeTruthy()
  })

  describe('Открытие/Скрытие саджеста', () => {
    test('Компонент с пустым списком не открывает саджест', () => {
      render(<TestSuggest items={[]} />)

      const input = screen.getByDisplayValue(initValue)
      fireEvent.focus(input)
      expect(screen.queryByRole('listbox')).toBeFalsy()
    })

    test('Компонент без значения в инпуте не открывает саджест', () => {
      render(<TestSuggest items={items} />)

      const input = screen.getByDisplayValue(initValue)
      fireEvent.change(input, { target: { value: '' } })
      fireEvent.focus(input)
      expect(screen.queryByRole('listbox')).toBeFalsy()
    })

    test('Инпут без фокуса не открывает саджест', () => {
      render(<TestSuggest items={items} />)

      expect(screen.queryByRole('listbox')).toBeFalsy()
    })

    test('Фокус на инпуте с непустым значением и непустым списком открывает саджест', async () => {
      render(<TestSuggest items={items} />)

      const input = screen.getByDisplayValue(initValue)
      fireEvent.focus(input)
      expect(screen.queryByRole('listbox')).toBeTruthy()
      const container = await screen.findByRole('combobox')
      checkAttributes(container, { 'aria-expanded': 'true' })
    })

    test('Снятие фокуса с инпута скрывает саджест', () => {
      render(<TestSuggest items={items} />)

      const input = screen.getByDisplayValue(initValue)
      fireEvent.focus(input)
      expect(screen.queryByRole('listbox')).toBeTruthy()
      fireEvent.blur(input)
      expect(screen.queryByRole('listbox')).toBeFalsy()
    })
  })

  describe('Использование горячих клавиш', () => {
    test('Перемещение стрелками вверх/вниз', async () => {
      render(<TestSuggest items={items} />)

      const input = screen.getByDisplayValue(initValue)
      fireEvent.focus(input)
      const container = await screen.findByRole('combobox')

      const item0 = screen.getByText(items[0].label)
      const item1 = screen.getByText(items[1].label)
      const item2 = screen.getByText(items[2].label)

      expect(item0.closest('[aria-selected="true"]')).toBeFalsy()
      fireEvent.keyUp(container, { key: 'ArrowDown' })
      expect(item0.closest('[aria-selected="true"]')).toBeTruthy()
      expect(screen.getByDisplayValue(items[0].label)).toBeTruthy()

      expect(item1.closest('[aria-selected="true"]')).toBeFalsy()
      fireEvent.keyUp(container, { key: 'ArrowDown' })
      expect(item0.closest('[aria-selected="true"]')).toBeFalsy()
      expect(item1.closest('[aria-selected="true"]')).toBeTruthy()
      expect(screen.getByDisplayValue(items[1].label)).toBeTruthy()

      fireEvent.keyUp(container, { key: 'ArrowUp' })
      expect(item0.closest('[aria-selected="true"]')).toBeTruthy()
      expect(item1.closest('[aria-selected="true"]')).toBeFalsy()
      expect(screen.getByDisplayValue(items[0].label)).toBeTruthy()

      fireEvent.keyUp(container, { key: 'ArrowUp' })
      expect(item2.closest('[aria-selected="true"]')).toBeFalsy()
      expect(item0.closest('[aria-selected="true"]')).toBeFalsy()
      expect(screen.getByDisplayValue(initValue)).toBeTruthy()

      fireEvent.keyUp(container, { key: 'ArrowUp' })
      expect(item2.closest('[aria-selected="true"]')).toBeTruthy()
      expect(screen.getByDisplayValue(items[2].label)).toBeTruthy()

      fireEvent.keyUp(container, { key: 'ArrowUp' })
      expect(item1.closest('[aria-selected="true"]')).toBeTruthy()
      expect(item2.closest('[aria-selected="true"]')).toBeFalsy()
      expect(screen.getByDisplayValue(items[1].label)).toBeTruthy()

      fireEvent.keyUp(container, { key: 'ArrowDown' })
      fireEvent.keyUp(container, { key: 'ArrowDown' })
      expect(item0.closest('[aria-selected="true"]')).toBeFalsy()
      expect(item2.closest('[aria-selected="true"]')).toBeFalsy()
      expect(screen.getByDisplayValue(initValue)).toBeTruthy()

      fireEvent.keyUp(container, { key: 'ArrowDown' })
      expect(item0.closest('[aria-selected="true"]')).toBeTruthy()
      expect(screen.getByDisplayValue(items[0].label)).toBeTruthy()

      fireEvent.keyUp(container, { key: 'ArrowDown' })
      expect(item1.closest('[aria-selected="true"]')).toBeTruthy()
      expect(item0.closest('[aria-selected="true"]')).toBeFalsy()
      expect(screen.getByDisplayValue(items[1].label)).toBeTruthy()
    })

    test('Перемещение стрелками вверх/вниз в списке из 1 элемента', async () => {
      render(<TestSuggest items={items.slice(0, 1)} />)

      const input = screen.getByDisplayValue(initValue)
      fireEvent.focus(input)
      const container = await screen.findByRole('combobox')

      const item0 = screen.getByText(items[0].label)

      expect(item0.closest('[aria-selected="true"]')).toBeFalsy()
      fireEvent.keyUp(container, { key: 'ArrowDown' })
      expect(item0.closest('[aria-selected="true"]')).toBeTruthy()
      expect(screen.getByDisplayValue(items[0].label)).toBeTruthy()

      fireEvent.keyUp(container, { key: 'ArrowDown' })
      expect(item0.closest('[aria-selected="true"]')).toBeFalsy()
      expect(screen.getByDisplayValue(initValue)).toBeTruthy()

      fireEvent.keyUp(container, { key: 'ArrowUp' })
      expect(item0.closest('[aria-selected="true"]')).toBeTruthy()
      expect(screen.getByDisplayValue(items[0].label)).toBeTruthy()
    })

    test('Работа с Escape', async () => {
      render(<TestSuggest items={items} />)

      const input = screen.getByDisplayValue(initValue)
      fireEvent.focus(input)
      const container = await screen.findByRole('combobox')
      fireEvent.keyUp(container, { key: 'Escape' })
      expect(screen.queryByRole('listbox')).toBeFalsy()

      fireEvent.keyUp(container, { key: 'ArrowDown' })
      expect(screen.queryByRole('listbox')).toBeTruthy()
      fireEvent.keyUp(container, { key: 'Escape' })
      expect(screen.queryByRole('listbox')).toBeFalsy()

      fireEvent.change(input, { target: { value: 'new' } })
      expect(screen.queryByRole('listbox')).toBeTruthy()
    })

    test('Выбор элемента через Enter', async () => {
      const handleSelectValue = jest.fn()
      render(<TestSuggest items={items} onSelectItem={handleSelectValue} />)

      const input = screen.getByDisplayValue(initValue)
      fireEvent.focus(input)
      const container = await screen.findByRole('combobox')
      fireEvent.keyUp(container, { key: 'ArrowDown' })
      fireEvent.keyUp(container, { key: 'Enter' })
      expect(handleSelectValue).toHaveBeenCalledWith(items[0])
      expect(screen.queryByRole('listbox')).toBeFalsy()
      expect(screen.getByDisplayValue('label0')).toBeTruthy()
    })

    test('При вводе вручную в инпут сбрасывается позиция в саджесте', async () => {
      render(<TestSuggest items={items} />)

      const input = screen.getByDisplayValue(initValue)
      fireEvent.focus(input)
      const container = await screen.findByRole('combobox')

      fireEvent.keyUp(container, { key: 'ArrowDown' })
      fireEvent.keyUp(container, { key: 'ArrowDown' })
      const newValue = 'new value'
      fireEvent.change(input, { target: { value: newValue } })

      fireEvent.keyUp(container, { key: 'ArrowDown' })
      expect(screen.getByDisplayValue(items[0].label)).toBeTruthy()
    })

    test('При вводе вручную в инпут и дальнейшем нажатии Escape сохраняется ручной ввод', async () => {
      render(<TestSuggest items={items} />)

      const input = screen.getByDisplayValue(initValue)
      fireEvent.focus(input)
      const container = await screen.findByRole('combobox')

      fireEvent.keyUp(container, { key: 'ArrowDown' })
      const newValue = 'new value'
      fireEvent.change(input, { target: { value: newValue } })
      fireEvent.keyUp(container, { key: 'Escape' })
      expect(screen.getByDisplayValue(newValue)).toBeTruthy()
    })
  })
})
