import { removeSearchFromUrl } from 'utils/remove-search-from-url'

interface Case {
  input: string
  output: string
}

const cases: Case[] = [
  {
    input: 'https://server/path',
    output: 'https://server/path',
  },
  {
    input: 'https://server/path?param1=value1&param2=value2&param1=value3',
    output: 'https://server/path',
  },
  {
    input: 'https://server/path?param1=value1&param2=value2&param1=value3=value1#hashValue',
    output: 'https://server/path#hashValue',
  },
  {
    input: 'https://server/path?param1=value1',
    output: 'https://server/path',
  },
  {
    input: 'https://server/path#hashValue',
    output: 'https://server/path#hashValue',
  },
]

describe('remove search url', () => {
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  test.each(cases)('Remove search from $input', ({ input, output }) => {
    const actual = removeSearchFromUrl(input)
    expect(actual).toEqual(output)
  })
})
