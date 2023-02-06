import {get, makeGet} from './get'
import {GetIn} from './get.types'

type TestData = {
  foo: {
    bar?: {
      barr: number[]
      bat: readonly [1, 2, 3]
      fal: false
      nul: null
      und?: unknown // к сожалению поля, тип которых является undefined, проходят проверку типизации :( поэтому эмулируем рандомное опциональное свойство
      str: string
      num: number
      obj: [
        {
          baz: number
        },
      ]
    }
  }
  primitive: number
}

const testData: TestData = {
  foo: {
    bar: {
      barr: [1, 2, 3],
      bat: [1, 2, 3] as const,
      fal: false,
      nul: null,
      und: undefined,
      str: '',
      num: 0,
      obj: [
        {
          baz: 123,
        },
      ],
    },
  },
  primitive: 123,
}

type Equals<X, Y> = (<T>() => T extends X ? 1 : 2) extends <T>() => T extends Y ? 1 : 2 ? true : false

type TestPath<Path extends string, T> = Equals<GetIn<TestData, Path>, T>

/**
 * Проверяем вывод типов. Если где-то что-то выводится неправильно, то этот интерфейс упадет с ошибкой
 */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
interface TypeTest extends Record<string, true> {
  'works with a single property': TestPath<'foo', TestData['foo']> | TestPath<'primitive', number>
  'works with dot-separated properties':
    | TestPath<'foo.bar', TestData['foo']['bar']>
    | TestPath<'foo.bar.barr', number[] | undefined>
  'works with indexed properties':
    | TestPath<'foo.bar.barr[1]', number | undefined>
    | TestPath<'foo.bar.barr[10]', number | undefined>
    | TestPath<'foo.bar.obj[0].baz', number | undefined>
  'works with tuples':
    | TestPath<'foo.bar.bat[1]', 2 | undefined>
    | TestPath<'foo.bar.bat[10]', undefined>
    | TestPath<'foo.bar.obj[0].baz', number | undefined>
  'works with nonexistent paths':
    | TestPath<'foo.bar.fal.asd.dsa.asd.dsa', undefined>
    | TestPath<'foo.bar.fal.asdasdasdasda', undefined>
    | TestPath<'foo.bar.nul.asd.dsa.asd.dsa', undefined>
    | TestPath<'foo.bar.nul.asdasdasdasda', undefined>
    | TestPath<'foo.bar.und.asd.dsa.asd.dsa', undefined>
    | TestPath<'foo.bar.und.asdasdasdasda', undefined>
    | TestPath<'foo.bar.str.asd.dsa.asd.dsa', undefined>
    | TestPath<'foo.bar.str.asdasdasdasda', undefined>
    | TestPath<'foo.bar.num.asd.dsa.asd.dsa', undefined>
    | TestPath<'foo.bar.num.asdasdasdasda', undefined>
    | TestPath<'foo.bar.barr[1].asd.dsa.asd.dsa', undefined>
    | TestPath<'foo.bar.barr[1].asdasdasdasda', undefined>
}

describe('`get` function', () => {
  it('works with a single property', () => {
    expect(get('primitive', testData)).toBe(testData.primitive)
    expect(get('foo', testData)).toBe(testData.foo)
  })

  it('works when getting stuff from undefined', () => {
    expect(get('foo.bar', undefined)).toBe(undefined)
    expect(get('foo.bar')(undefined)).toBe(undefined)
  })

  it('works with dot-separated properties', () => {
    expect(get('foo.bar', testData)).toBe(testData.foo.bar)
    expect(get('foo.bar.barr', testData)).toBe(testData.foo.bar?.barr)
  })

  it('works with indexed properties', () => {
    expect(get('foo.bar.barr[1]', testData)).toBe(testData.foo.bar?.barr[1])
    expect(get('foo.bar.barr[10]', testData)).toBe(testData.foo.bar?.barr[10])
    expect(get('foo.bar.obj[0].baz', testData)).toBe(testData.foo.bar?.obj[0].baz)
  })

  it('works with tuples', () => {
    expect(get('foo.bar.bat[1]', testData)).toBe(testData.foo.bar?.bat[1])
    // проверяем что попытка доступа к несуществующему элементу кортежа ломается
    // @ts-expect-error
    expect(get('foo.bar.bat[10]', testData)).toBe(testData.foo.bar.bat[10])
    expect(get('foo.bar.obj[0].baz', testData)).toBe(testData.foo.bar?.obj[0].baz)
  })

  it('correctly retrieves falsy values', () => {
    expect(get('foo.bar.fal', testData)).toBe(false)
    expect(get('foo.bar.nul', testData)).toBe(null)
    expect(get('foo.bar.und', testData)).toBe(undefined)
    expect(get('foo.bar.str', testData)).toBe('')
    expect(get('foo.bar.num', testData)).toBe(0)
  })

  it('works with nonexistent paths', () => {
    // проверяем поведение в рантайме и проверяем ошибки типизации (они должны быть, иначе ts-expect-error стрельнет)
    // @ts-expect-error
    expect(get('foo.bar.fal.asd.dsa.asd.dsa', testData)).toBe(undefined)
    // @ts-expect-error
    expect(get('foo.bar.fal.asdasdasdasda', testData)).toBe(undefined)
    // @ts-expect-error
    expect(get('foo.bar.nul.asd.dsa.asd.dsa', testData)).toBe(undefined)
    // @ts-expect-error
    expect(get('foo.bar.nul.asdasdasdasda', testData)).toBe(undefined)
    // @ts-expect-error
    expect(get('foo.bar.und.asd.dsa.asd.dsa', testData)).toBe(undefined)
    // @ts-expect-error
    expect(get('foo.bar.und.asdasdasdasda', testData)).toBe(undefined)
    // @ts-expect-error
    expect(get('foo.bar.str.asd.dsa.asd.dsa', testData)).toBe(undefined)
    // @ts-expect-error
    expect(get('foo.bar.str.asdasdasdasda', testData)).toBe(undefined)
    // @ts-expect-error
    expect(get('foo.bar.num.asd.dsa.asd.dsa', testData)).toBe(undefined)
    // @ts-expect-error
    expect(get('foo.bar.num.asdasdasdasda', testData)).toBe(undefined)
    // @ts-expect-error
    expect(get('foo.bar.barr[1].asd.dsa.asd.dsa', testData)).toBe(undefined)
    // @ts-expect-error
    expect(get('foo.bar.barr[1].asdasdasdasda', testData)).toBe(undefined)
  })

  it('can have fixed type via `makeGet`', () => {
    const getFromTest = makeGet<TestData>()

    expect(getFromTest('foo.bar', testData)).toBe(get('foo.bar', testData))
    // @ts-expect-error
    expect(getFromTest('asdasdasdasd', testData)).toBe(get('asdasdasdasd', testData))
    // @ts-expect-error
    expect(getFromTest('foo.bar', {})).toBe(undefined)
    expect(getFromTest('foo.bar.obj[0].baz', testData)).toBe(get('foo.bar.obj[0].baz', testData))
    // проверка типов
    // @ts-expect-error
    getFromTest('asdasdasd')
    getFromTest('foo.bar')
  })
})
