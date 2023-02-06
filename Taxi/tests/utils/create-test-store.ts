import {noop} from '@lavka/utils'

import {createStore} from '../../src/lib/createStore'
import {Catalog, Common, ProductTags} from '../../src/models'

export function createTestStore() {
  return createStore({
    productTags: new ProductTags({
      loginAndSave: noop,
    }),
    catalog: new Catalog({
      modes: ['grocery'],
    }),
    common: new Common({
      getMetrikaPlaceInfo: () => {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        return {} as any
      },
      useShouldAnimateControls() {
        return false
      },
    }),
  })
}
