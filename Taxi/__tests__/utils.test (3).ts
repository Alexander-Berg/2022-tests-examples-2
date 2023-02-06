import {fixUri, isCorrectGeoPoint} from '../utils'

describe('fixUri', () => {
  it('do nothing without lon, lat and uri', () => {
    const uri = fixUri({source: 'GEO_REQUEST'})

    expect(uri).toBe(undefined)
  })
  it('do nothing without lon and lat', () => {
    const uri = fixUri({source: 'GEO_REQUEST', uri: 'hop hey lalaley'})

    expect(uri).toBe('hop hey lalaley')
  })
  it('do nothing without lon', () => {
    const uri = fixUri({source: 'GEO_REQUEST', lat: 1, uri: 'hop hey lalaley'})

    expect(uri).toBe('hop hey lalaley')
  })
  it('do nothing without lat', () => {
    const uri = fixUri({source: 'GEO_REQUEST', lon: 1, uri: 'hop hey lalaley'})

    expect(uri).toBe('hop hey lalaley')
  })
  it('works only with yandex maps protocol in uri', () => {
    const uri = 'gmaps://place_id=ChIJddYBQt9x5kcR7u6ZEVuCxW0'
    const fixedUri = fixUri({source: 'GEO_REQUEST', lon: 1, lat: 1, uri})

    expect(uri).toBe(fixedUri)
  })
  it('works', () => {
    const wrongIncomingUri = 'ymapsbm1://geo?ll=1%2C2&spn=0.001%2C0.001&text=any'
    const fixedUri = fixUri({source: 'GEO_REQUEST', lon: 2, lat: 1, uri: wrongIncomingUri})

    expect(fixedUri).not.toBe(wrongIncomingUri)
    expect(fixedUri).toBe('ymapsbm1://geo?ll=2%2C1&spn=0.001%2C0.001&text=any')
  })
})

describe('isCorrectGeoPoint', () => {
  it('works correct with null/undef', () => {
    expect(isCorrectGeoPoint(null)).toBe(false)
    expect(isCorrectGeoPoint(undefined)).toBe(false)
  })
  it('works correct with empty object', () => {
    expect(isCorrectGeoPoint({})).toBe(false)
  })
  it('works correct with zero integer values', () => {
    expect(isCorrectGeoPoint({lon: 0, lat: 0})).toBe(true)
  })
  it('works correct if coords partially exists', () => {
    expect(isCorrectGeoPoint({lon: 1, uri: 'eee'})).toBe(true)
  })
  it('works fine in happy scenarios', () => {
    expect(isCorrectGeoPoint({lon: 1, lat: 1})).toBe(true)
    expect(isCorrectGeoPoint({uri: 'eee'})).toBe(true)
    expect(isCorrectGeoPoint({fullAddress: 'улица Пушкина'})).toBe(true)
  })
})
