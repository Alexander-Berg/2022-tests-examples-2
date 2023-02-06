import { getSearchFromUrl } from 'utils/getSearchFromUrl'

interface Case {
  url: string
  search: string | undefined
}

const cases: Case[] = [
  {
    url: 'https://server/path',
    search: undefined,
  },
  {
    url: 'https://server/path#hash',
    search: undefined,
  },
  {
    url: 'https://server/path#hash1#hash2',
    search: undefined,
  },
  {
    url: 'https://server/index?param1=value1',
    search: '?param1=value1',
  },
  {
    url: 'https://server/index?param1=value1#hash',
    search: '?param1=value1',
  },
  {
    url: 'https://server/index?param1=value1#hash1#hash2',
    search: '?param1=value1',
  },
  {
    url: 'server/path',
    search: undefined,
  },
  {
    url: 'server/path#hash',
    search: undefined,
  },
  {
    url: 'server/path#hash1#hash2',
    search: undefined,
  },
  {
    url: 'server/index?param1=value1',
    search: '?param1=value1',
  },
  {
    url: 'server/index?param1=value1#hash',
    search: '?param1=value1',
  },
  {
    url: 'server/index?param1=value1#hash1#hash2',
    search: '?param1=value1',
  },
]

describe('get search from url', () => {
  test.each(cases)('Extract $search from $url', ({ url, search }) => {
    const actual = getSearchFromUrl(url)
    expect(actual).toEqual(search)
  })
})
