/**
 * пишем результаты в output, чтобы могли подхватить следующие таски
 */
import {writeResultResource} from '../../lib/ci'
import {Deploy} from '../../lib/ci/deploy'
import {prepareDeployDataToSend, DeployEnv} from '../../lib/clownductor'
import {assertEnv, exitError} from '../../lib/util'

const {
  BRANCH_NAME,
  BUILD_ENV,
  BUILD_RESOURCE_ID,
  BUILD_RESOURCE_PATH,
  BUILD_RESOURCE_TYPE,
  BUILD_TASK_ID,
  BUILD_TASK_TYPE,
  PROJECT_NAME,
  SANDBOX_TOKEN,
} = assertEnv(
  'BRANCH_NAME',
  'BUILD_ENV',
  'BUILD_RESOURCE_ID',
  'BUILD_RESOURCE_PATH',
  'BUILD_RESOURCE_TYPE',
  'BUILD_TASK_ID',
  'BUILD_TASK_TYPE',
  'PROJECT_NAME',
  'SANDBOX_TOKEN',
)

const {BUILD_IMAGE = ''} = process.env

handle().catch(exitError)

async function handle() {
  const deploy = new Deploy({
    projectName: PROJECT_NAME,
    branchName: BRANCH_NAME,
    buildEnv: BUILD_ENV as DeployEnv,
    buildImage: BUILD_IMAGE,
    sandboxToken: SANDBOX_TOKEN,
    releaseIssue: process.env.RELEASE_ISSUE,
    clownductorToken: 'DUMMY_TOKEN',
    buildResource: {
      resourceId: BUILD_RESOURCE_ID,
      resourcePath: BUILD_RESOURCE_PATH,
      taskId: BUILD_TASK_ID,
      taskType: BUILD_TASK_TYPE,
      type: BUILD_RESOURCE_TYPE,
    },
  })

  const deployBody = await deploy.getDeployBody()

  await deploy.appendBadges()

  writeResultResource('deploy_clownductor_body', JSON.stringify(prepareDeployDataToSend(deployBody)))
}
