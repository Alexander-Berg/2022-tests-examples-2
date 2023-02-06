import {UpdateCheckStatusRequest} from '@yandex-int/si.ci.arcanum-api'

import StatusEnum = UpdateCheckStatusRequest.StatusEnum

import {config} from '../../config'
import {createCheck} from '../../lib/arcanum'
import {assertEnv, exitError} from '../../lib/util'

const {PULL_REQUEST_ID, DIFF_SET_ID} = assertEnv('PULL_REQUEST_ID', 'DIFF_SET_ID')

handle().catch(exitError)

async function handle() {
  const pullRequestId = parseInt(PULL_REQUEST_ID)
  const diffSetId = parseInt(DIFF_SET_ID)
  await createCheck({
    pullRequestId,
    diffSetId,
    check: {
      system: config.namespace,
      type: 'sample_check',
      status: StatusEnum.Pending,
      description: 'тестовый статус',
      system_check_uri: 'https://ya.ru/',
    },
  })
}
