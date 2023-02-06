import {act} from '@testing-library/react'

import {delay} from '@lavka/utils'

/**
 * В тестах возникает ошибка если вызвать
 *
 * await delay(n)
 *
 * Warning: An update to TestComponent inside a test was not wrapped in act(...).
 * When testing, code that causes React state updates should be wrapped into act(...):
 */
export async function actWait(time: number) {
  await act(() => delay(time))
}
