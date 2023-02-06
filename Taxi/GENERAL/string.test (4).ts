import {lpad, camelToSnake, snakeToCamel} from './string'

import {ToCamel, ToCamelSafe, ToSnake, ToSnakeSafe} from './string.types'

interface Err<T extends string> {
  toString(): T
}

function createSnakeToCamelTest<Snake extends string, Camel extends string>(
  snake: Snake,
  camel: Camel,
): Camel extends ToCamel<Snake>
  ? Camel extends ToCamelSafe<Snake>
    ? Snake extends ToSnake<Camel>
      ? Snake extends ToSnakeSafe<Camel>
        ? [Snake, Camel]
        : Err<'ToSnakeSafe'>
      : Err<'ToSnake'>
    : Err<'ToCamelSafe'>
  : Err<'ToCamel'> {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return [snake, camel] as any
}

function createSnakeToCamelSafeTest<Snake extends string, Camel extends string>(
  snake: Snake,
  camel: Camel,
): Camel extends ToCamelSafe<Snake>
  ? Snake extends ToSnakeSafe<Camel>
    ? [Snake, Camel]
    : Err<'ToSnakeSafe'>
  : Err<'ToCamelSafe'> {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return [snake, camel] as any
}

const TESTS: [string, string][] = [
  createSnakeToCamelTest('', ''),
  createSnakeToCamelTest('a', 'a'),
  createSnakeToCamelTest('ab', 'ab'),
  createSnakeToCamelTest('_ab', 'Ab'),
  createSnakeToCamelTest('a_b', 'aB'),
  createSnakeToCamelTest('_a_b', 'AB'),
  createSnakeToCamelTest('_a', 'A'),
  createSnakeToCamelTest('test_case', 'testCase'),
  createSnakeToCamelTest('test2_case', 'test2Case'),
  createSnakeToCamelTest('a__b', 'a_B'),
  createSnakeToCamelTest('a__', 'a__'),
  createSnakeToCamelTest('a_b', 'aB'),
  createSnakeToCamelTest('__a', '_A'),
  createSnakeToCamelTest('category-group-shortcut-id', 'category-group-shortcut-id'),
  createSnakeToCamelTest('lavka-frontend_desktop_mobile', 'lavka-frontendDesktopMobile'),
]

const SAFE_TEST: [string, string][] = [
  createSnakeToCamelSafeTest('a_1c', '$a_1c'),
  createSnakeToCamelSafeTest('A_b', '$A_b'),
  createSnakeToCamelSafeTest('a_B', '$a_B'),
  createSnakeToCamelSafeTest('A', '$A'),
  createSnakeToCamelSafeTest('AB', '$AB'),
]

describe('lib', () => {
  describe('string', () => {
    describe('lpad', () => {
      it('should work', () => {
        const res = lpad('hello', 20, '  ')
        expect(res).toBe('               hello')
      })
    })

    describe('cases', () => {
      it('to snake', () => {
        for (const item of TESTS) {
          const str = camelToSnake(item[1])
          const res: typeof str = item[0]
          expect(str).toBe(res)
        }
      })
      it('to camel', () => {
        for (const item of TESTS) {
          const str = snakeToCamel(item[0])
          const res: typeof str = item[1]
          expect(str).toBe(res)
        }
      })
      it('to snake safe', () => {
        for (const item of SAFE_TEST) {
          const str = camelToSnake(item[1], true)
          const res: typeof str = item[0]
          expect(str).toBe(res)
        }
      })
      it('to camel safe', () => {
        for (const item of SAFE_TEST) {
          const str = snakeToCamel(item[0], true)
          const res: typeof str = item[1]
          expect(str).toBe(res)
        }
      })
    })
  })
})
