import {maxByDataKeys, getPlaceholder, getPointsLineWithDelta, formatToPoints, formatPointDateString} from './utils'
import {
  mockFormatPointDateString,
  mockFormatToPoints,
  mockGetPointsLineWithDelta,
  mockMaxByDataKeys
} from './__tests__/mock'
import {Chart} from './types'

describe('getPlaceholder', () => {
  it('If charts array, result should be "Пока нет данных"', () => {
    const charts: Chart[] = []
    expect(getPlaceholder(charts)).toBe('Пока нет данных')
  })

  it('If charts string, result should be string value of charts', () => {
    const charts = 'Не доступно для данной грануляции'
    expect(getPlaceholder(charts)).toBe(charts)
  })
})

describe('maxByDataKeys', () => {
  const {chartPoints, dataKeys, stacked} = mockMaxByDataKeys.cases[0]

  it('if NOT stacked result should be max value of chartId', () => {
    expect(maxByDataKeys(chartPoints, dataKeys)).toBe(330)
  })

  it('if stacked result should be max value of sum chartId by dateString', () => {
    expect(maxByDataKeys(chartPoints, dataKeys, stacked)).toBe(390)
  })
})

describe('formatPointDateString', () => {
  it('if chunkingPeriod NOT interval, result should be dt_form', () => {
    const {date, chunkingPeriod} = mockFormatPointDateString.cases[0]
    expect(formatPointDateString(date, chunkingPeriod)).toBe(date.dt_from)
  })

  it('if chunkPeriod === interval, result should be dt_from-dt_to in dd.mm.yy format', () => {
    const {date, chunkingPeriod, result} = mockFormatPointDateString.cases[1]
    expect(formatPointDateString(date, chunkingPeriod)).toBe(result)
  })
})

describe('getPointsLineWithDelta', () => {
  it('Should be return array of coordinates where x: date, y: value', () => {
    const {charts, chunkingPeriod, result} = mockGetPointsLineWithDelta.cases[0]

    expect(getPointsLineWithDelta(charts as Chart[], chunkingPeriod)).toEqual(result)
  })

  it('Should be return array of coordinates where x: date, y: value', () => {
    const {charts, chunkingPeriod, result} = mockGetPointsLineWithDelta.cases[1]

    expect(getPointsLineWithDelta(charts as Chart[], chunkingPeriod)).toEqual(result)
  })
})

describe('formatToPoints', () => {
  it('Should return array of objects, where dateString is dateId and last keys is id of charts', () => {
    const {charts, dataKeys, chunkingPeriod, result} = mockFormatToPoints.cases[0]
    expect(formatToPoints(charts as Chart[], dataKeys, chunkingPeriod)).toEqual(result)
  })

  it('Should return array of objects, where dateString is dateId and last keys is id of charts', () => {
    const {charts, dataKeys, chunkingPeriod, result} = mockFormatToPoints.cases[1]
    expect(formatToPoints(charts as Chart[], dataKeys, chunkingPeriod)).toEqual(result)
  })
})
