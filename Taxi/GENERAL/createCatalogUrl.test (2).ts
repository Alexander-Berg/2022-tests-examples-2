import type { Locale } from 'types/common'
import { createCatalogUrl } from 'utils/createCatalogUrl'

interface Param {
  id: string
  deepLink?: string
  deep_link?: string
}

interface Case {
  input: {
    locale: Locale | string | undefined
    city: number | string | undefined
    category: Param | string | undefined
    subcategory: Param | string | undefined
    good: Param | string | undefined
  }
  output: string
}

const cases: Case[] = [
  {
    input: {
      locale: undefined,
      city: undefined,
      category: 'categoryId',
      subcategory: undefined,
      good: undefined,
    },
    output: '/category/categoryId',
  },
  {
    input: {
      locale: undefined,
      city: undefined,
      category: 'categoryId  ',
      subcategory: undefined,
      good: undefined,
    },
    output: '/category/categoryId%20%20',
  },
  {
    input: {
      locale: 'locale',
      city: undefined,
      category: 'categoryId',
      subcategory: undefined,
      good: undefined,
    },
    output: '/locale/category/categoryId',
  },
  {
    input: {
      locale: 'locale',
      city: 'city',
      category: 'categoryId',
      subcategory: undefined,
      good: undefined,
    },
    output: '/locale/city/category/categoryId',
  },
  {
    input: {
      locale: 'locale',
      city: 'city',
      category: {
        id: 'categoryId',
      },
      subcategory: undefined,
      good: undefined,
    },
    output: '/locale/city/category/categoryId',
  },
  {
    input: {
      locale: 'locale',
      city: 'city',
      category: {
        id: 'categoryId',
        deepLink: 'categoryAlias',
      },
      subcategory: undefined,
      good: undefined,
    },
    output: '/locale/city/category/categoryAlias',
  },
  {
    input: {
      locale: 'locale',
      city: 'city',
      category: {
        id: 'categoryId',
        deepLink: '',
      },
      subcategory: undefined,
      good: undefined,
    },
    output: '/locale/city/category/categoryId',
  },
  {
    input: {
      locale: 'locale',
      city: 'city',
      category: undefined,
      subcategory: undefined,
      good: undefined,
    },
    output: '/locale/city',
  },
  {
    input: {
      locale: 'locale',
      city: 'city',
      category: 'categoryId',
      subcategory: 'subcategoryId',
      good: undefined,
    },
    output: '/locale/city/category/categoryId/subcategoryId',
  },
  {
    input: {
      locale: 'locale',
      city: 'city',
      category: 'categoryId',
      subcategory: {
        id: 'subcategoryId',
      },
      good: undefined,
    },
    output: '/locale/city/category/categoryId/subcategoryId',
  },
  {
    input: {
      locale: 'locale',
      city: 'city',
      category: 'categoryId',
      subcategory: {
        id: 'subcategoryId',
        deepLink: 'subcategoryAlias',
      },
      good: undefined,
    },
    output: '/locale/city/category/categoryId/subcategoryAlias',
  },
  {
    input: {
      locale: 'locale',
      city: 'city',
      category: 'categoryId',
      subcategory: {
        id: 'subcategoryId',
        deepLink: '',
      },
      good: undefined,
    },
    output: '/locale/city/category/categoryId/subcategoryId',
  },
  {
    input: {
      locale: 'locale',
      city: 'city',
      category: 'categoryId',
      subcategory: 'subcategoryId',
      good: 'goodId',
    },
    output: '/locale/city/category/categoryId/subcategoryId/goods/goodId',
  },
  {
    input: {
      locale: 'locale',
      city: 'city',
      category: 'categoryId',
      subcategory: 'subcategoryId',
      good: {
        id: 'goodId',
      },
    },
    output: '/locale/city/category/categoryId/subcategoryId/goods/goodId',
  },
  {
    input: {
      locale: 'locale',
      city: 'city',
      category: 'categoryId',
      subcategory: 'subcategoryId',
      good: {
        id: 'goodId',
        deepLink: 'goodAlias',
      },
    },
    output: '/locale/city/category/categoryId/subcategoryId/goods/goodAlias',
  },
  {
    input: {
      locale: 'locale',
      city: 'city',
      category: 'categoryId',
      subcategory: 'subcategoryId',
      good: {
        id: 'goodId',
        deepLink: '',
      },
    },
    output: '/locale/city/category/categoryId/subcategoryId/goods/goodId',
  },
  {
    input: {
      locale: 'locale',
      city: 'city',
      category: 'categoryId',
      subcategory: undefined,
      good: 'goodId',
    },
    output: '/locale/city/category/categoryId/goods/goodId',
  },
  {
    input: {
      locale: 'locale',
      city: 'city',
      category: undefined,
      subcategory: 'subcategoryId',
      good: 'goodId',
    },
    output: '/locale/city/good/goodId',
  },
  {
    input: {
      locale: 'locale',
      city: 'city',
      category: {
        id: 'categoryId',
        deep_link: 'categoryAlias',
      },
      subcategory: undefined,
      good: undefined,
    },
    output: '/locale/city/category/categoryAlias',
  },
  {
    input: {
      locale: 'locale',
      city: 'city',
      category: {
        id: 'categoryId',
        deep_link: '',
      },
      subcategory: undefined,
      good: undefined,
    },
    output: '/locale/city/category/categoryId',
  },
  {
    input: {
      locale: 'locale',
      city: 'city',
      category: 'categoryId',
      subcategory: {
        id: 'subcategoryId',
        deep_link: 'subcategoryAlias',
      },
      good: undefined,
    },
    output: '/locale/city/category/categoryId/subcategoryAlias',
  },
  {
    input: {
      locale: 'locale',
      city: 'city',
      category: 'categoryId',
      subcategory: {
        id: 'subcategoryId',
        deep_link: '',
      },
      good: undefined,
    },
    output: '/locale/city/category/categoryId/subcategoryId',
  },
  {
    input: {
      locale: 'locale',
      city: 'city',
      category: 'categoryId',
      subcategory: 'subcategoryId',
      good: {
        id: 'goodId',
        deep_link: 'goodAlias',
      },
    },
    output: '/locale/city/category/categoryId/subcategoryId/goods/goodAlias',
  },
  {
    input: {
      locale: 'locale',
      city: 'city',
      category: 'categoryId',
      subcategory: 'subcategoryId',
      good: {
        id: 'goodId',
        deep_link: '',
      },
    },
    output: '/locale/city/category/categoryId/subcategoryId/goods/goodId',
  },
]

describe('create catalog url', () => {
  test.each(cases)(
    'Create url from $input.locale / $input.city / $input.category / $input.subcategory / $input.good',
    ({ input, output }) => {
      const actual = createCatalogUrl(input)
      expect(actual).toEqual(output)
    },
  )
})
