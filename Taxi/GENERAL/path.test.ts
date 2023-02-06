import {GetIn} from './get.types'
import {ObjectWithPath, PathsIn, PathsWithTarget} from './path'

interface TestData {
  obj: {
    field: number
    array: number[]
    objArray: {foo: number}[]
    tuple: readonly [number, string, symbol]
    tupleObj: readonly [{foo: number}, {bar: string}, {baz: symbol}]
    optional?: {
      num: number
      str?: string
    }
  }
}

type TestPaths = PathsIn<TestData>
type TestPathsInclude<T> = T extends TestPaths ? true : false
type TestPathsExclude<T> = T extends TestPaths ? false : true

interface TestPathsIn extends Record<string, true> {
  'supports dot access': TestPathsInclude<'obj.field'>
  'supports arrays': TestPathsInclude<'obj.array[0]'> | TestPathsInclude<`obj.array[${number}]`>
  'supports objects within arrays': TestPathsInclude<'obj.objArray[0].foo'>
  'supports tuples':
    | TestPathsInclude<'obj.tuple[0]' | 'obj.tuple[1]' | 'obj.tuple[2]'>
    | TestPathsExclude<'obj.tuple[3]' | `obj.tuple[${number}]`>
  'supports object within tuples':
    | TestPathsInclude<'obj.tupleObj[0].foo' | 'obj.tupleObj[1].bar' | 'obj.tupleObj[2].baz'>
    | TestPathsExclude<'obj.tupleObj[0].bar' | 'obj.tupleObj[2].foo'>
}

type AccessorInTestData<S extends string> = TestData extends ObjectWithPath<S> ? true : false
type AccessorNotInTestData<S extends string> = TestData extends ObjectWithPath<S> ? false : true

interface TestObjectWithPath extends Record<string, true> {
  'works with objects': AccessorInTestData<'obj'> | AccessorInTestData<'obj.field'>
  'works with arrays': AccessorInTestData<'obj.array[0]'>
  'works with tuples': AccessorInTestData<'obj.tuple[0]'> | AccessorNotInTestData<'obj.tuple[3]'>
  'works with nested structures':
    | AccessorInTestData<'obj.objArray[12].foo'>
    | AccessorInTestData<'obj.tupleObj[0].foo'>
    | AccessorInTestData<'obj.tupleObj[1].bar'>
  'works with optional paths': AccessorInTestData<'obj.optional.num'> | AccessorInTestData<'obj.optional.str'>
}

type TestDataHasTargetByPath<Target, Path extends string> = Target extends GetIn<TestData, Path>
  ? Path extends PathsWithTarget<TestData, Target>
    ? true
    : false
  : 'false'

interface TestPathsWithTarget extends Record<string, true> {
  'works with primitive types':
    | TestDataHasTargetByPath<number, 'obj.field'>
    | TestDataHasTargetByPath<symbol, 'obj.tuple[2]'>
  'works with arrays': TestDataHasTargetByPath<number[], 'obj.array'>
  'works with tuples': TestDataHasTargetByPath<readonly [number, string, symbol], 'obj.tuple'>
  'works with shapes':
    | TestDataHasTargetByPath<{foo: number}, 'obj.tupleObj[0]'>
    | TestDataHasTargetByPath<{foo: number}, `obj.objArray[${number}]`>
  'works with optional properties':
    | TestDataHasTargetByPath<{num: number; str?: string}, 'obj.optional'>
    | TestDataHasTargetByPath<string, 'obj.optional.str'>
}

describe('Typecheck successful', () => {
  it('is only a type', () => {})
})
