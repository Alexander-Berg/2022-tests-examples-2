import {lpad} from '.'

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
