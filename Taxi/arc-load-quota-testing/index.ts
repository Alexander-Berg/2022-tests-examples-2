/**
 * создаёт X пулл-реквестов с рандомным изменением и периодически обновляет их
 * можно протестировать сколько квоты уходит на X пулл-реквестов
 *
 * @example
 *
 * создать 15 пулл-реквестов:
 * npx ts-node --transpile-only ./tools/command/arc-load-quota-testing/index.ts
 *
 * разово обновить эти пулл-реквесты и запустить таймер на обновление каждые 3 минуты
 * npx ts-node --transpile-only ./tools/command/arc-load-quota-testing/index.ts -u
 *
 * очистить эти пулл-реквесты
 * npx ts-node --transpile-only ./tools/command/arc-load-quota-testing/index.ts -c
 */
import {strict as assert} from 'assert'
import path from 'path'

import execa from 'execa'

import {cleanupPullRequests} from './cleanup'
import {createPullRequests} from './create'
import {updatePullRequests} from './update'

console.log(`cwd: ${process.cwd()}`)
const currentChanges = JSON.parse(execa.sync('arc', ['st', '--json']).stdout)

assert(Object.keys(currentChanges.status).length === 0, 'есть незакоммиченные изменения')

const {argv} = process

const RESULT_FILE = path.join(__dirname, 'result.json')
const IS_UPDATE = argv.includes('-u') || argv.includes('--update')
const IS_CLEANUP = argv.includes('-c') || argv.includes('--cleanup')
const PULL_REQUEST_COUNT = 15
const UPDATE_INTERVAL = 60_000 * 3

const start = () => {
  if (IS_CLEANUP) {
    cleanupPullRequests(RESULT_FILE)
  } else if (IS_UPDATE) {
    updatePullRequests(UPDATE_INTERVAL, RESULT_FILE)
  } else {
    createPullRequests(PULL_REQUEST_COUNT, RESULT_FILE)
  }
}

start()
