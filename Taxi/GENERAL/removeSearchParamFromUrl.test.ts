import { removeSearchParamFromUrl } from 'utils/removeSearchParamFromUrl'

interface Case {
  param: string
  input: string
  output: string
}

const cases: Case[] = [
  {
    param: '',
    input: 'https://server/path',
    output: 'https://server/path',
  },
  {
    param: '',
    input: 'https://server/path?param1=value1&param2=value2&param1=value3',
    output: 'https://server/path?param1=value1&param2=value2&param1=value3',
  },
  {
    param: '',
    input: 'https://server/path?param1=value1&param2=value2&param1=value3=value1#hashValue',
    output: 'https://server/path?param1=value1&param2=value2&param1=value3=value1#hashValue',
  },
  {
    param: 'param1',
    input: 'https://server/path?param1=value1&param2=value2&param1=value3',
    output: 'https://server/path?param2=value2',
  },
  {
    param: 'param2',
    input: 'https://server/path?param1=value1&param2=value2&param1=value3',
    output: 'https://server/path?param1=value1&param1=value3',
  },
  {
    param: 'param3',
    input: 'https://server/path?param1=value1&param2=value2&param1=value3#hashValue',
    output: 'https://server/path?param1=value1&param2=value2&param1=value3#hashValue',
  },
  {
    param: 'param1',
    input: 'https://server/path?param1=value1&param2=value2&param1=value3#hashValue',
    output: 'https://server/path?param2=value2#hashValue',
  },
  {
    param: 'param2',
    input: 'https://server/path?param1=value1&param2=value2&param1=value3#hashValue',
    output: 'https://server/path?param1=value1&param1=value3#hashValue',
  },
  {
    param: 'param3',
    input: 'https://server/path?param1=value1&param2=value2&param1=value3#hashValue',
    output: 'https://server/path?param1=value1&param2=value2&param1=value3#hashValue',
  },
  {
    param: 'param1',
    input: 'https://server/path?param1=value1',
    output: 'https://server/path',
  },
]

describe('remove search param from  url', () => {
  test.each(cases)('Remove "$param" from $input', ({ param, input, output }) => {
    const actual = removeSearchParamFromUrl(input, param)
    expect(actual).toEqual(output)
  })
})
