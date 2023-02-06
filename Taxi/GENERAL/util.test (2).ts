import {insertedComparedElement} from './util'

describe('insertedComparedElement utility function', () => {
  it('should insert an element inside an empty array regardless of comparator results', () => {
    const emptyArray: number[] = []
    expect(insertedComparedElement(emptyArray, 1, () => 1)).toEqual([1])
    expect(insertedComparedElement(emptyArray, 1, () => 0)).toEqual([1])
    expect(insertedComparedElement(emptyArray, 1, () => -1)).toEqual([1])
  })

  it('should insert an element at index where element and arr[index] comparison return 1', () => {
    const array = [101, 78, 203, 11, 22, -1]
    expect(insertedComparedElement(array, 33, (arrEl, insertedEl) => (insertedEl > arrEl ? 1 : -1)))
  })

  it('should insert an element at last index of first range where element and arr[index] comparison returned only 0', () => {
    const array = [101, 56, 78, 11, 22, 34]
    expect(insertedComparedElement(array, 33, (arrEl, insertedEl) => (insertedEl > arrEl ? 0 : -1))).toEqual([
      101, 56, 78, 11, 22, 33, 34,
    ])

    const array2 = [101, 56, 78, 11, 22, 34, 0, 57]
    expect(insertedComparedElement(array2, 33, (arrEl, insertedEl) => (insertedEl > arrEl ? 0 : -1))).toEqual([
      101, 56, 78, 11, 22, 33, /* <- at the end of the first range [11, 22] */ 34, 0,
      /* <- not at i + 1 index of the last zero-comparison of sequence */ 57,
    ])
  })
})
