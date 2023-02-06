import {
  ARIA_DISABLED,
  DATA_ANIMATION_STATE,
  DATA_CHECKED,
  DATA_DISABLED,
  DATA_ID,
  DATA_ITEM_ID,
  DATA_ITEM_TYPE,
  DATA_LOADING,
  DATA_TEST_ID,
  DATA_VALUE,
  DATA_VALUE_STATUS,
} from '@lavka/constants'

const createDataAttrGetter = (name: string) => {
  const builder = (querySelector: string) => {
    return `[${name}="${querySelector}"]`
  }

  return (querySelector: string) => {
    const data = querySelector.split(' ')
    if (data.length > 1) {
      return data.map(builder).join(' ')
    }

    return builder(querySelector)
  }
}

export const mkAriaDisabled = createDataAttrGetter(ARIA_DISABLED)
export const mkDataAnimationState = createDataAttrGetter(DATA_ANIMATION_STATE)
export const mkDataChecked = createDataAttrGetter(DATA_CHECKED)
export const mkDataDisabled = createDataAttrGetter(DATA_DISABLED)
export const mkDataId = createDataAttrGetter(DATA_ID)
export const mkDataItemId = createDataAttrGetter(DATA_ITEM_ID)
export const mkDataItemType = createDataAttrGetter(DATA_ITEM_TYPE)
export const mkDataLoading = createDataAttrGetter(DATA_LOADING)
export const mkDataValue = createDataAttrGetter(DATA_VALUE)
export const mkDataValueStatus = createDataAttrGetter(DATA_VALUE_STATUS)
export const mkTestId = createDataAttrGetter(DATA_TEST_ID)
