import { stringFloatSchema } from './schemas'

describe('schemas/stringFloatSchema', () => {
  test('Positive cases', () => {
    const positiveCasesWithoutSign = ['0', '0.', '0.1', '.1', '01']
    const positiveCasesWithMinusSign = positiveCasesWithoutSign.map((str) => '-' + str)
    const positiveCasesWithPlusSign = positiveCasesWithoutSign.map((str) => '+' + str)

    const allPositiveCases = [...positiveCasesWithoutSign, ...positiveCasesWithMinusSign, ...positiveCasesWithPlusSign]

    for (const str of allPositiveCases) {
      expect(stringFloatSchema.isValidSync(str)).toBe(true)
    }
  })

  test('Negative cases', () => {
    const negativeCases = ['', '.', '1a', 'a1', '--1', '++1', '-+1', '+-1']

    for (const str of negativeCases) {
      expect(stringFloatSchema.isValidSync(str)).toBe(false)
    }
  })
})
