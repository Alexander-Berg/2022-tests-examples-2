import createAction from '@player2/utils/action'

describe('Action creator', () => {
  interface Payload {
    a: number[]
  }

  it('Should properly create action without creator function', () => {
    const action = createAction<string>('someType')('payload')
    expect(action).toEqual({
      type: 'someType',
      payload: 'payload',
    })
  })

  it('Should properly create action with creator function', () => {
    const action = createAction<Payload>(
      'someType',
      (...args: number[]) => {
        return {
          a: args,
        }
      }
    )(1, 2, 3)
    expect(action).toEqual({
      type: 'someType',
      payload: {a: [1, 2, 3]},
    })
  })
})
