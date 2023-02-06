import { removeLastSlashFromUrl } from 'utils/remove-last-slash-from-url'

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
    output: 'https://server/path?param1=value1&param2=value2&param1=value3',
  },
  {
    input: 'https://server/path?param1=value1&param2=value2&param1=value3=value1#hashValue',
    output: 'https://server/path?param1=value1&param2=value2&param1=value3=value1#hashValue',
  },
  {
    input: 'https://server/path?param1=value1',
    output: 'https://server/path?param1=value1',
  },
  {
    input: 'https://server/path#hashValue',
    output: 'https://server/path#hashValue',
  },
  {
    input: 'https://server/path/',
    output: 'https://server/path',
  },
  {
    input: 'https://server/path/?param1=value1&param2=value2&param1=value3',
    output: 'https://server/path?param1=value1&param2=value2&param1=value3',
  },
  {
    input: 'https://server/path/?param1=value1&param2=value2&param1=value3=value1#hashValue',
    output: 'https://server/path?param1=value1&param2=value2&param1=value3=value1#hashValue',
  },
  {
    input: 'https://server/path/?param1=value1',
    output: 'https://server/path?param1=value1',
  },
  {
    input: 'https://server/path/#hashValue',
    output: 'https://server/path#hashValue',
  },
]

describe('remove last slash from url', () => {
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  test.each(cases)('Remove last slash from $input', ({ input, output }) => {
    const actual = removeLastSlashFromUrl(input)
    expect(actual).toEqual(output)
  })
})
