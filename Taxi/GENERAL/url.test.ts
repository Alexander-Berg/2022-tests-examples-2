// Current directory
import {isEqualUrls} from '.'

describe('lib', () => {
  describe('url', () => {
    describe('isEqualUrls', () => {
      it('should return true on two full urls', () => {
        const leftUrl = 'https://example.com/a/b/c?foo=bar&bar=foo&baz=bar'
        const rightUrl = 'https://example.com/a/b/c?baz=bar&bar=foo&foo=bar'

        expect(isEqualUrls(leftUrl, rightUrl)).toEqual(true)
      })

      it('should return true on part of url with querystring and full url', () => {
        const leftUrl = '/a/b/c?foo=bar&bar=foo&baz=bar'
        const rightUrl = 'https://example.com/a/b/c?baz=bar&bar=foo&foo=bar'

        expect(isEqualUrls(leftUrl, rightUrl)).toEqual(true)
      })

      it('should return false on urls with different query params', () => {
        const leftUrl = '/a/b/c?foo=bar&bar=foo&baz=bar'
        const rightUrl = 'https://example.com/a/b/c?baz=test&bar=kek'

        expect(isEqualUrls(leftUrl, rightUrl)).toEqual(false)
      })
    })
  })
})
