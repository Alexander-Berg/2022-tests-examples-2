/* tslint:disable:newline-per-chained-call */

import {lpad} from './index'

describe('lib', () => {
  describe('string', () => {
    describe('lpad', () => {
      it('should work', () => {
        const res = lpad('hello', 20, '  ')

        expect(res).toBe('               hello')
      })
    })
  })
})
