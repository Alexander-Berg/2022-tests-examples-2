/**
 * файл временно переименован в tes.ts, т.к. ломается об top-level await из модуля @webview/utils/webp
 */
import {isEqualUrls} from './parse'

describe('url', () => {
  describe('isEqualUrls', () => {
    it('should return true on two full urls', () => {
      const leftUrl = 'https://example.com/a/b/c?foo=bar&bar=foo&baz=bar'
      const rightUrl = 'https://example.com/a/b/c?baz=bar&bar=foo&foo=bar'

      expect(isEqualUrls(leftUrl, rightUrl)).toEqual(true)
    })

    it('should return false on urls with different query params', () => {
      const leftUrl = 'https://example.com/a/b/c?foo=bar&bar=foo&baz=bar'
      const rightUrl = 'https://example.com/a/b/c?baz=test&bar=kek'

      expect(isEqualUrls(leftUrl, rightUrl)).toEqual(false)
    })
  })
})
