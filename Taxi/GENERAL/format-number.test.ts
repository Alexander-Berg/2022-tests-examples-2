import {formatNumber} from './format-number'

const SPACE = String.fromCharCode(0x00a0)

describe('Разделение чисел по разрядам и замена разделителей дробной части', () => {
  test('Россия', () => {
    expect(formatNumber('10000.50 рублей')).toEqual(`10${SPACE}000,50 рублей`)
    expect(formatNumber('Купить за 1000000 рублей')).toEqual(`Купить за 1${SPACE}000${SPACE}000 рублей`)
    expect(formatNumber('Купить 1000 шт за 1000000 рублей')).toEqual(
      `Купить 1${SPACE}000 шт за 1${SPACE}000${SPACE}000 рублей`,
    )
    expect(formatNumber(1000)).toEqual(`1${SPACE}000`)
    expect(formatNumber(1000.12)).toEqual(`1${SPACE}000,12`)
  })
  test('Англия', () => {
    expect(formatNumber('EUR 10000.50', 'en')).toEqual('EUR 10,000.50')
    expect(formatNumber('EUR 10000,50', 'en')).toEqual('EUR 10,000.50')
    expect(formatNumber(1000, 'en')).toEqual('1,000')
    expect(formatNumber(1000.12, 'en')).toEqual('1,000.12')
  })
})
