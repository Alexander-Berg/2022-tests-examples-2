import type { Address } from 'types/address'

import { getFullAddress, getShortAddress, getShortAddressInfo } from './format'

const fullAddress: Address = {
  coordinates: [0, 0] as Coordinates,
  country: 'country',
  city: 'city',
  full: 'full',
  street: 'street',
  house: 'house',
  title: 'title',
}

describe('addressFormat', () => {
  describe('getFullAddress - Страна, Город, Улица, Дом', () => {
    it('Есть все поля', () => {
      expect(getFullAddress(fullAddress)).toBe('country, city, street, house')
    })

    it('Поля частично отсутствуют', () => {
      {
        // нет улицы - используем title
        const { street: _street, ...address } = fullAddress
        expect(getFullAddress(address)).toBe('country, city, title')
      }
      {
        // и title нет - используем full - он некрасиво избыточен, но там скорее всего есть вся информация
        const { street: _street, title: _title, ...address } = fullAddress
        expect(getFullAddress(address)).toBe('full')
      }
      {
        // и full нет - используем что есть
        const { street: _street, title: _title, full: _full, ...address } = fullAddress
        expect(getFullAddress(address)).toBe('country, city, house')
      }
    })
  })

  describe('getShortAddress - Улица, Дом', () => {
    it('Есть все поля', () => {
      expect(getShortAddress(fullAddress)).toBe('street, house')
    })

    it('Поля частично отсутствуют', () => {
      {
        // нет улицы - используем title
        const { street: _street, ...address } = fullAddress
        expect(getShortAddress(address)).toBe('title')
      }
      {
        // и title нет - пишем город, дом
        const { street: _street, title: _title, ...address } = fullAddress
        expect(getShortAddress(address)).toBe('city, house')
      }
    })
  })

  describe('getShortAddressInfo', () => {
    it('Есть все поля', () => {
      expect(getShortAddressInfo(fullAddress)).toEqual({
        street: 'street',
        house: 'house',
        text: 'street, house',
      })
    })

    it('Поля частично отсутствуют', () => {
      {
        // нет улицы - используем title
        const { street: _street, ...address } = fullAddress
        expect(getShortAddressInfo(address)).toEqual({
          street: 'title',
          text: 'title',
        })
      }
      {
        // и title нет - пишем город, дом
        const { street: _street, title: _title, ...address } = fullAddress
        expect(getShortAddressInfo(address)).toEqual({
          street: 'city',
          house: 'house',
          text: 'city, house',
        })
      }
    })
  })
})
