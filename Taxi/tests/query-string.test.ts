import {qs} from '../query-string'

describe('query-string', () => {
  test("parses x=y to {x: 'y'}", () => {
    const data = qs.parse('x=y')
    expect(data.x).toBe('y')
  })

  test("parses x=1&t=2 to {x: '1', y: '2'}", () => {
    const data = qs.parse('x=1&t=2')
    expect(data.x).toBe('1')
    expect(data.t).toBe('2')
  })

  test("stringifies {x: 'y'} to x=y", () => {
    const str = qs.stringify({x: 'y'})
    expect(str).toBe('x=y')
  })

  test("stringifies {x: '1', y: '2'} to x=1&y=2 or y=2&x=1 ", () => {
    const str = qs.stringify({x: 1, y: 2})
    const sortedParts = str.split('&').sort()
    expect(sortedParts[0]).toBe('x=1')
    expect(sortedParts[1]).toBe('y=2')
  })
})
