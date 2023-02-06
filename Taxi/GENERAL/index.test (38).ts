import Sandbox from '@yandex-int/sandboxer'
import dayjs from 'dayjs'
import nock from 'nock'

import {config, SandboxResource} from '../../../../config'
import {DeployEnv} from '../../../../lib/clownductor'
import {RESOURCE_INFINITY_TTL} from '../../../../lib/sandbox'
import {assertEnv} from '../../../../lib/util'

import {lxcContainer} from './lxc-container'
import {nodejsBinaries} from './nodejs-binaries'
import {npmCache} from './npm-cache'
import {projectBuild} from './project-build'

describe('handle-resources-ttl: handler', () => {
  let sandbox: Sandbox

  beforeAll(() => {
    nock.disableNetConnect()
    nock.enableNetConnect(/localhost/)
  })

  afterAll(() => {
    nock.enableNetConnect()
  })

  beforeEach(() => {
    const {SANDBOX_TOKEN} = assertEnv('SANDBOX_TOKEN')
    sandbox = new Sandbox({
      token: SANDBOX_TOKEN,
      retry: {
        minTimeout: 0,
        maxTimeout: 0,
      },
    })
  })

  afterEach(() => {
    nock.cleanAll()
  })

  it('should remove stale "npm-cache" resources', async () => {
    const items = [...Array(5)].map((_, ix) => {
      return {
        id: ix + 1,
        time: {
          created: dayjs().toISOString(),
        },
        attributes: {
          ttl: RESOURCE_INFINITY_TTL,
        },
      }
    })

    nock(`${config.sandbox.host}`)
      .get('/api/v1.0/resource')
      .query(({type}) => type === SandboxResource.LAVKA_FRONTEND_NPM_CACHE)
      .reply(200, {total: items.length, items})

    const {important, changes} = await npmCache.handle({sandbox})

    expect(important.map(({resource}) => resource.id)).toEqual([1, 2, 3])

    expect(changes.map(({resource}) => resource.id)).toEqual([4, 5])
    expect(changes.map(({ttl}) => ttl)).toEqual([...Array(2)].fill(npmCache.STALE_TTL))
  })

  it('should remove stale "project-build" resources', async () => {
    const items = [
      {
        id: 1,
        time: {
          created: dayjs().subtract(13, 'months').toISOString(),
        },
        attributes: {
          env: DeployEnv.PRODUCTION,
          ttl: 10,
        },
      },
      {
        id: 2,
        time: {
          created: dayjs().subtract(13, 'months').toISOString(),
        },
        attributes: {
          env: DeployEnv.TESTING,
          ttl: RESOURCE_INFINITY_TTL,
        },
      },
      {
        id: 3,
        time: {
          created: dayjs().subtract(13, 'months').toISOString(),
        },
        attributes: {
          env: DeployEnv.UNSTABLE,
          ttl: RESOURCE_INFINITY_TTL,
        },
      },
    ]

    nock(`${config.sandbox.host}`)
      .get('/api/v1.0/resource')
      .query(({type}) => type === SandboxResource.LAVKA_FRONTEND_PROJECT_BUILD)
      .reply(200, {total: items.length, items})

    const {important, changes} = await projectBuild.handle({sandbox})

    expect(important.map(({resource}) => resource.id)).toEqual([1])

    expect(changes.map(({resource}) => resource.id)).toEqual([2, 3])
    expect(changes.map(({ttl}) => ttl)).toEqual([
      projectBuild.ENV_OPTIONS[DeployEnv.TESTING].STALE_TTL,
      projectBuild.ENV_OPTIONS[DeployEnv.UNSTABLE].STALE_TTL,
    ])
  })

  it('should remove stale "nodejs-binaries" resources', async () => {
    const items = [...Array(8)].map((_, ix) => {
      return {
        id: ix + 1,
        time: {
          created: dayjs().toISOString(),
        },
        attributes: {
          ttl: RESOURCE_INFINITY_TTL,
          version: ix < 2 ? config.images_manifest.node_version : `0.0.${ix}`,
        },
      }
    })

    nock(`${config.sandbox.host}`)
      .get('/api/v1.0/resource')
      .query(({type}) => type === SandboxResource.LAVKA_FRONTEND_NODEJS_BINARIES)
      .reply(200, {total: items.length, items})

    const {important, changes} = await nodejsBinaries.handle({sandbox})

    expect(important.map(({resource}) => resource.id)).toEqual([1, 3, 4, 5, 6])

    expect(changes.map(({resource}) => resource.id)).toEqual([2, 7, 8])
    expect(changes.map(({ttl}) => ttl)).toEqual([...Array(3)].fill(nodejsBinaries.STALE_TTL))
  })

  it('should remove stale "lxc-container" resources', async () => {
    const items = [...Array(5)].map((_, ix) => {
      return {
        id: !ix ? config.sandbox_container_resource_id : ix + 1,
        time: {
          created: dayjs().toISOString(),
        },
        attributes: {
          ttl: 300,
        },
      }
    })

    nock(`${config.sandbox.host}`)
      .get('/api/v1.0/resource')
      .query(({type}) => type === SandboxResource.LXC_CONTAINER)
      .reply(200, {total: items.length, items})

    const {important, changes} = await lxcContainer.handle({sandbox})

    expect(important.map(({resource}) => resource.id)).toEqual([config.sandbox_container_resource_id, 2, 3])

    expect(changes.map(({resource}) => resource.id)).toEqual([4, 5])
    expect(changes.map(({ttl}) => ttl)).toEqual([...Array(2)].fill(lxcContainer.STALE_TTL))
  })
})
