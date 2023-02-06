import {BuildDataItem} from '../types'

import * as getBuildsInfoModule from './get-builds-info'
import {ReleasesChecker} from './releases-checker'

describe('notifier class', () => {
  const mockSecretPaths = {
    issuerId: 'any-path',
    keyId: 'any-path',
    keyContent: 'any-path',
  }

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('test collectData with no passed persisted data and start date', async () => {
    const startDate = '2022-02-04T02:19:59-08:00'

    const options = [
      {
        appName: 'App name 1',
        chatIds: [-123],
        appId: 'appId-1',
        startTime: startDate,
        secrets: mockSecretPaths,
      },
      {
        appName: 'App name 2',
        chatIds: [-234, -123],
        appId: 'appId-2',
        startTime: startDate,
        secrets: mockSecretPaths,
      },
    ]

    jest.spyOn(getBuildsInfoModule, 'getBuildsInfo').mockImplementation(({appId}) => {
      if (appId === 'appId-1') {
        return Promise.resolve([
          {
            appId: 'appId-1',
            appStoreState: 'IN_REVIEW',
            build: '0.1.2',
            createdDate: '2022-03-04T02:19:59-08:00',
            platform: 'IOS',
          },
          {
            appId: 'appId-1',
            appStoreState: 'IN_REVIEW',
            build: '0.1.1',
            createdDate: '2022-01-04T02:19:59-08:00',
            platform: 'IOS',
          },
        ] as BuildDataItem[])
      }
      return Promise.resolve([
        {
          appId: 'appId-2',
          appStoreState: 'PREORDER_READY_FOR_SALE',
          build: '1.2.1',
          createdDate: '2022-04-04T02:19:59-08:00',
          platform: 'IOS',
        },
      ] as BuildDataItem[])
    })

    const notifier = new ReleasesChecker({options, persistedData: []})

    const {collectedData, collectedMessages} = await notifier.collectData()

    expect(collectedData).toStrictEqual([
      {
        appId: 'appId-1',
        appStoreState: 'IN_REVIEW',
        build: '0.1.2',
        createdDate: '2022-03-04T02:19:59-08:00',
        platform: 'IOS',
      },
      {
        appId: 'appId-1',
        appStoreState: 'IN_REVIEW',
        build: '0.1.1',
        createdDate: '2022-01-04T02:19:59-08:00',
        platform: 'IOS',
      },
      {
        appId: 'appId-2',
        appStoreState: 'PREORDER_READY_FOR_SALE',
        build: '1.2.1',
        createdDate: '2022-04-04T02:19:59-08:00',
        platform: 'IOS',
      },
    ])

    expect(collectedMessages).toStrictEqual([
      {
        chatId: '-123',
        messages: [
          '[App name 1]\n' +
            'IOS: 0.1.2 2022-03-04T02:19:59-08:00. Начинаем слежение за сборкой. Текущий state в магазине: IN_REVIEW\n',
          '[App name 2]\n' +
            'IOS: 1.2.1 2022-04-04T02:19:59-08:00. Начинаем слежение за сборкой. Текущий state в магазине: PREORDER_READY_FOR_SALE\n',
        ],
      },
      {
        chatId: '-234',
        messages: [
          '[App name 2]\n' +
            'IOS: 1.2.1 2022-04-04T02:19:59-08:00. Начинаем слежение за сборкой. Текущий state в магазине: PREORDER_READY_FOR_SALE\n',
        ],
      },
    ])
  })

  it('test collectData with passed persisted data and start date', async () => {
    const startDate = '2022-01-01T02:19:59-08:00'

    const options = [
      {
        appName: 'App name 1',
        chatIds: [-123],
        appId: 'appId-1',
        startTime: startDate,
        secrets: mockSecretPaths,
      },
      {
        appName: 'App name 2',
        chatIds: [-234, -123],
        appId: 'appId-2',
        startTime: startDate,
        secrets: mockSecretPaths,
      },
    ]

    jest.spyOn(getBuildsInfoModule, 'getBuildsInfo').mockImplementation(({appId}) => {
      if (appId === 'appId-1') {
        return Promise.resolve([
          {
            appId: 'appId-1',
            appStoreState: 'IN_REVIEW',
            build: '0.1.2',
            createdDate: '2022-03-04T02:19:59-08:00',
            platform: 'IOS',
          },
          {
            appId: 'appId-1',
            appStoreState: 'IN_REVIEW',
            build: '0.1.1',
            createdDate: '2022-01-04T02:19:59-08:00',
            platform: 'IOS',
          },
        ] as BuildDataItem[])
      }
      return Promise.resolve([
        {
          appId: 'appId-2',
          appStoreState: 'PREORDER_READY_FOR_SALE',
          build: '1.2.1',
          createdDate: '2022-04-04T02:19:59-08:00',
          platform: 'IOS',
        },
        {
          appId: 'appId-2',
          appStoreState: 'PREPARE_FOR_SUBMISSION',
          build: '1.3.1',
          createdDate: '2022-04-04T02:19:59-08:00',
          platform: 'IOS',
        },
      ] as BuildDataItem[])
    })

    const notifier = new ReleasesChecker({
      options,
      persistedData: [
        {
          appId: 'appId-1',
          appStoreState: 'PENDING_CONTRACT',
          build: '0.1.2',
          createdDate: '2022-03-04T02:19:59-08:00',
          platform: 'IOS',
        },
        {
          appId: 'appId-2',
          appStoreState: 'PREORDER_READY_FOR_SALE',
          build: '1.2.1',
          createdDate: '2022-04-04T02:19:59-08:00',
          platform: 'IOS',
        },
      ],
    })

    const {collectedData, collectedMessages} = await notifier.collectData()

    expect(collectedData).toStrictEqual([
      {
        appId: 'appId-1',
        appStoreState: 'IN_REVIEW',
        build: '0.1.2',
        createdDate: '2022-03-04T02:19:59-08:00',
        platform: 'IOS',
      },
      {
        appId: 'appId-1',
        appStoreState: 'IN_REVIEW',
        build: '0.1.1',
        createdDate: '2022-01-04T02:19:59-08:00',
        platform: 'IOS',
      },
      {
        appId: 'appId-2',
        appStoreState: 'PREORDER_READY_FOR_SALE',
        build: '1.2.1',
        createdDate: '2022-04-04T02:19:59-08:00',
        platform: 'IOS',
      },
      {
        appId: 'appId-2',
        appStoreState: 'PREPARE_FOR_SUBMISSION',
        build: '1.3.1',
        createdDate: '2022-04-04T02:19:59-08:00',
        platform: 'IOS',
      },
    ])

    expect(collectedMessages).toStrictEqual([
      {
        chatId: '-123',
        messages: [
          '[App name 1]\n' +
            'IOS: 0.1.2 2022-03-04T02:19:59-08:00. Build изменил state в магазине: PENDING_CONTRACT->IN_REVIEW\n' +
            'IOS: 0.1.1 2022-01-04T02:19:59-08:00. Появилась новая версия сборки. Текущий state в магазине: IN_REVIEW\n',
          '[App name 2]\n' +
            'IOS: 1.3.1 2022-04-04T02:19:59-08:00. Появилась новая версия сборки. Текущий state в магазине: PREPARE_FOR_SUBMISSION\n',
        ],
      },
      {
        chatId: '-234',
        messages: [
          '[App name 2]\n' +
            'IOS: 1.3.1 2022-04-04T02:19:59-08:00. Появилась новая версия сборки. Текущий state в магазине: PREPARE_FOR_SUBMISSION\n',
        ],
      },
    ])
  })
})
