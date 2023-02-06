import type {
  DiscountPricing,
  ProductAttribute,
  StickerInfo,
} from '@lavka/api-typings/uservices/grocery-api/definitions'

import type { ProductCardSticker } from './types'
import { getStickersFromProduct } from './utils'

const getStickersText: (...args: Parameters<typeof getStickersFromProduct>) => string[] = (...args) => {
  return getStickersFromProduct(...args).map(({ text }) => text)
}

const baseProps = {
  text_color: 'white',
  sticker_color: 'green',
}

describe('modesUtils', () => {
  describe('getStickersFromProduct', () => {
    it('Нет стикеров', () => {
      expect(getStickersText(undefined, undefined, undefined)).toEqual([])
    })

    it('Только инфостикеры. Есть ограничения', () => {
      const infoStickers: StickerInfo[] = [
        {
          ...baseProps,
          text: 'XL portion',
        },
        {
          ...baseProps,
          text: 'XL',
        },
        {
          ...baseProps,
          text: 'XL longlonglonglong',
        },
        {
          ...baseProps,
          text: 'XL port',
        },
      ]

      const expected = ['XL', 'XL port', 'XL portion']
      expect(getStickersText(infoStickers, undefined, undefined, 3)).toEqual(expected)
    })

    it('Нет скидки. Есть инфостикеры. Есть теги. Нет ограничений', () => {
      const infoStickers: StickerInfo[] = [
        {
          ...baseProps,
          text: 'XL portion',
        },
        {
          ...baseProps,
          text: 'XL',
        },
      ]

      const attributeStickers: ProductAttribute[] = [
        {
          title: 'Fish',
          attribute: '',
        },
        {
          title: 'Cat',
          attribute: '',
        },
      ]

      const expected: ProductCardSticker['text'][] = ['XL', 'XL portion', 'Fish', 'Cat']
      expect(getStickersText(infoStickers, undefined, attributeStickers)).toEqual(expected)
    })

    it('Есть скидка. Есть инфостикеры. Есть теги. Нет ограничений', () => {
      const discountPricing: DiscountPricing = {
        discount_label: '-10%',
      }

      const infoStickers: StickerInfo[] = [
        {
          ...baseProps,
          text: 'XL portion',
        },
        {
          ...baseProps,
          text: 'XL',
        },
      ]

      const attributeStickers: ProductAttribute[] = [
        {
          title: 'Fish',
          attribute: '',
        },
        {
          title: 'Cat',
          attribute: '',
        },
      ]

      const expected: ProductCardSticker['text'][] = ['XL', '-10%', 'XL portion', 'Fish', 'Cat']
      expect(getStickersText(infoStickers, discountPricing, attributeStickers)).toEqual(expected)
    })

    it('Есть скидка. Есть инфостикеры. Есть теги. Есть ограничения', () => {
      const discountPricing: DiscountPricing = {
        discount_label: '-10%',
      }

      const infoStickers: StickerInfo[] = [
        {
          ...baseProps,
          text: 'XL portion',
        },
        {
          ...baseProps,
          text: 'XL port',
        },
      ]

      const attributeStickers: ProductAttribute[] = [
        {
          title: 'Fish',
          attribute: '',
        },
        {
          title: 'Cat',
          attribute: '',
        },
      ]

      const expected: ProductCardSticker['text'][] = ['-10%', 'XL port', 'XL portion']
      expect(getStickersText(infoStickers, discountPricing, attributeStickers, 3)).toEqual(expected)
    })

    it('Есть длинная скидка. Есть инфостикеры. Нет тегов. Есть ограничения', () => {
      const discountPricing: DiscountPricing = {
        discount_label: '-1234567890%',
      }

      const infoStickers: StickerInfo[] = [
        {
          ...baseProps,
          text: 'XL port',
        },
        {
          ...baseProps,
          text: 'XL portion',
        },
        {
          ...baseProps,
          text: 'XL p',
        },
      ]

      const expected: ProductCardSticker['text'][] = ['XL p', 'XL port', '-1234567890%']
      expect(getStickersText(infoStickers, discountPricing, undefined, 3)).toEqual(expected)
    })

    it('Есть длинная скидка. Есть инфостикеры. Есть теги. Есть ограничения', () => {
      const discountPricing: DiscountPricing = {
        discount_label: '-1234567890%',
      }

      const infoStickers: StickerInfo[] = [
        {
          ...baseProps,
          text: 'XL port',
        },
        {
          ...baseProps,
          text: 'XL portion-portion',
        },
        {
          ...baseProps,
          text: 'XL p',
        },
      ]

      const attributeStickers: ProductAttribute[] = [
        {
          title: 'Fish',
          attribute: '',
        },
        {
          title: 'Cat',
          attribute: '',
        },
      ]

      const expected: ProductCardSticker['text'][] = ['XL p', 'XL port', '-1234567890%', 'XL portion-portion']
      expect(getStickersText(infoStickers, discountPricing, attributeStickers, 4)).toEqual(expected)
    })
  })
})
