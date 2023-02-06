import {getUniqBuildId} from './get-uniq-build-id'

describe('getUniqBuildId util', () => {
  it('should get correct id', () => {
    const dataItem = {
      platform: 'IOS',
      createdDate: 'any',
      build: '0.0.1',
      appStoreState: 'PREORDER_READY_FOR_SALE',
      appId: '123',
    }
    expect(getUniqBuildId(dataItem)).toBe('123-0.0.1')
  })
})
