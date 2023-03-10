import {makeComplexHeader} from '.'

describe('make-complex-header', () => {
  it('should support url encoded keys and values', () => {
    expect(makeComplexHeader({ключ: 'значение'})).toBe(
      '%D0%BA%D0%BB%D1%8E%D1%87=%D0%B7%D0%BD%D0%B0%D1%87%D0%B5%D0%BD%D0%B8%D0%B5',
    )
  })
  it('should support multiple keys', () => {
    expect(makeComplexHeader({a: 'b', c: 'd'})).toBe('a=b,c=d')
  })
  it('should skip empty values', () => {
    expect(makeComplexHeader({a: undefined, b: null, c: ''})).toBe('')
  })
})
