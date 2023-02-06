import {mergePersistedData} from './merge-persisted-data'
import {BuildDataItem} from './types'

describe('mergeAppStoreData util', () => {
  it('should correct merge data', () => {
    const items: BuildDataItem[] = [
      {appId: '2', appStoreState: 'IN_REVIEW', build: '0.0.1', createdDate: 'any', platform: 'IOS'},
    ]
    const prevItems: BuildDataItem[] = [
      {appId: '1', appStoreState: 'ACCEPTED', build: '0.0.1', createdDate: 'any', platform: 'IOS'},
      {appId: '2', appStoreState: 'PREORDER_READY_FOR_SALE', build: '0.0.2', createdDate: 'any', platform: 'IOS'},
      {appId: '2', appStoreState: 'PREPARE_FOR_SUBMISSION', build: '0.0.1', createdDate: 'any', platform: 'IOS'},
    ]

    expect(mergePersistedData(prevItems, items)).toStrictEqual([
      {appId: '1', appStoreState: 'ACCEPTED', build: '0.0.1', createdDate: 'any', platform: 'IOS'},
      {appId: '2', appStoreState: 'PREORDER_READY_FOR_SALE', build: '0.0.2', createdDate: 'any', platform: 'IOS'},
      {appId: '2', appStoreState: 'IN_REVIEW', build: '0.0.1', createdDate: 'any', platform: 'IOS'},
    ])
  })
  it('should correct merge data with no previous', () => {
    const items: BuildDataItem[] = [
      {appId: '2', appStoreState: 'IN_REVIEW', build: '0.0.1', createdDate: 'any', platform: 'IOS'},
    ]
    expect(mergePersistedData([], items)).toStrictEqual([
      {appId: '2', appStoreState: 'IN_REVIEW', build: '0.0.1', createdDate: 'any', platform: 'IOS'},
    ])
  })
})
