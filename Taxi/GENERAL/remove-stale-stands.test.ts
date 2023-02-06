import {integer, word, url} from 'casual'
import dayjs from 'dayjs'
import {noop} from 'lodash'
import nock from 'nock'

import {config} from '../../config'
import {ServiceBranch} from '../../lib/clownductor'
import * as vault from '../../lib/vault'

import {handle as removeStaleStands, DAYS_TO_STALE} from './remove-stale-stands'

const ARCANUM_HOST = 'https://a.yandex-team.ru'
const CLOWNDUCTOR_HEADERS = {
  'X-YaTaxi-Api-Key': 'clownductor-token',
}

const SERVICE_BRANCHES: ServiceBranch[] = [
  {
    id: integer(),
    service_id: integer(),
    name: word,
    env: 'unstable',
    direct_link: url,
    configs: [],
    endpointsets: [],
  },
  {
    id: integer(),
    service_id: integer(),
    name: 'dev-pr8164',
    env: 'unstable',
    direct_link: url,
    configs: [],
    endpointsets: [],
  },
  {
    id: 123,
    service_id: integer(),
    name: 'dev-pr2291411',
    env: 'unstable',
    direct_link: url,
    configs: [],
    endpointsets: [],
  },
]

const CLOSED_PR = {
  data: {
    state: 'closed',
    updated_at: '2022-02-02T15:21:52.231408Z',
  },
}

const OPENED_PR = {
  data: {
    state: 'open',
    updated_at: '2022-02-02T15:21:52.231408Z',
  },
}

describe('remove stale stands', () => {
  beforeAll(() => {
    nock.disableNetConnect()
    nock.enableNetConnect(/localhost/)
  })

  afterAll(() => {
    nock.enableNetConnect()
  })

  beforeEach(() => {
    nock(config.clownductor.host).get('/api/branches/').query(true).reply(200, SERVICE_BRANCHES).persist()
    nock(config.clownductor.host, {reqheaders: CLOWNDUCTOR_HEADERS})
      .post('/v1/remove_dev_branch/', body => {
        expect(body).toEqual({branch_id: 123})
        return body
      })
      .reply(200, {
        job_id: 456,
      })
      .persist()

    const getVersionValues: typeof vault['getVersionValues'] = (..._input) => Promise.resolve({foo: 'bar'} as never)
    jest.spyOn(vault, 'getVersionValues').mockImplementationOnce(getVersionValues)
  })

  afterEach(() => {
    nock.cleanAll()
  })

  it('should remove stale stands', async () => {
    nock(ARCANUM_HOST).get('/api/v1/review-requests/2291411').query(true).reply(200, CLOSED_PR).persist()

    const report = await removeStaleStands(noop)

    expect(report.get()).toEqual([
      'website (pr:2291411): closed',
      'website (branch:dev-pr2291411): remove job id 456',
      'webview (pr:2291411): closed',
      'webview (branch:dev-pr2291411): remove job id 456',
      'dev-api (pr:2291411): closed',
      'dev-api (branch:dev-pr2291411): remove job id 456',
    ])
  })

  it('should handle days to stale env', () => {
    expect(DAYS_TO_STALE).toEqual(5)
    expect(DAYS_TO_STALE === config.stand_days_to_stale).toBeFalsy()
  })

  it('should handle days to stale pass', async () => {
    nock(ARCANUM_HOST)
      .get('/api/v1/review-requests/2291411')
      .query(true)
      .reply(200, {
        ...OPENED_PR,
        data: {
          ...OPENED_PR.data,
          updated_at: dayjs().subtract(DAYS_TO_STALE, 'days').add(1, 'hour').toISOString(),
        },
      })
      .persist()

    const report = await removeStaleStands(noop)

    expect(report.get()).toEqual([
      'website (pr:2291411): pass',
      'website: no stands found',
      'webview (pr:2291411): pass',
      'webview: no stands found',
      'dev-api (pr:2291411): pass',
      'dev-api: no stands found',
    ])
  })

  it('should handle days to stale remove', async () => {
    const updated_at = dayjs()
      .subtract(DAYS_TO_STALE + 1, 'days')
      .toISOString()

    nock(ARCANUM_HOST)
      .get('/api/v1/review-requests/2291411')
      .query(true)
      .reply(200, {
        ...OPENED_PR,
        data: {
          ...OPENED_PR.data,
          updated_at,
        },
      })
      .persist()

    const report = await removeStaleStands(noop)

    expect(report.get()).toEqual([
      `website (pr:2291411): stale 6.00 (updated at ${updated_at})`,
      'website (branch:dev-pr2291411): remove job id 456',
      `webview (pr:2291411): stale 6.00 (updated at ${updated_at})`,
      'webview (branch:dev-pr2291411): remove job id 456',
      `dev-api (pr:2291411): stale 6.00 (updated at ${updated_at})`,
      'dev-api (branch:dev-pr2291411): remove job id 456',
    ])
  })
})
