import {get as getByPath} from 'lodash'

import {serviceYaml} from '../../lib/ci'
import {deploy, DeployEnv, waitJob} from '../../lib/clownductor'
import {getRuntimeAttrs} from '../../lib/nanny'
import {assertEnv, exitError, getProjectImageTag} from '../../lib/util'

const {
  CLOWNDUCTOR_TOKEN,
  NANNY_TOKEN,
  BUILD_RELEASE,
  BUILD_RESOURCE_ID,
  BUILD_RESOURCE_TYPE,
  BUILD_TASK_ID,
  BUILD_TASK_TYPE,
  BUILD_RESOURCE_PATH,
  PROJECT_NAME,
} = assertEnv([
  'CLOWNDUCTOR_TOKEN',
  'NANNY_TOKEN',
  'BUILD_RELEASE',
  'BUILD_RESOURCE_ID',
  'BUILD_RESOURCE_TYPE',
  'BUILD_TASK_ID',
  'BUILD_TASK_TYPE',
  'BUILD_RESOURCE_PATH',
  'PROJECT_NAME',
])

// TODO: rm
console.log('PARAMS:', {
  CLOWNDUCTOR_TOKEN,
  BUILD_RELEASE,
  BUILD_RESOURCE_ID,
  BUILD_RESOURCE_TYPE,
  BUILD_TASK_ID,
  BUILD_TASK_TYPE,
  BUILD_RESOURCE_PATH,
})

const SERVICE_NAME = serviceYaml.getServiceName()

// TODO: undo
// deployRtcStub().catch(exitError);
// handle2().catch(exitError);
handle().catch(exitError)

async function _deployRtcStub() {
  const res = await deploy({
    env: BUILD_RELEASE as DeployEnv,
    serviceName: SERVICE_NAME,
    token: CLOWNDUCTOR_TOKEN,
    dockerImage: `lavka/website/${BUILD_RELEASE}:stub`,
  })

  console.log(res)
}

async function _handle2(deployBoth = false) {
  const dockerImage = await statDockerImage()
  console.log('dockerImage:', dockerImage) // TODO: rm

  if (deployBoth) {
    const {job_id} = await deployProjectBuildResource()

    await waitJob(job_id, {maxAttempts: 180, delay: 10000})

    const {deploy_link} = await deployProjectDockerImage(dockerImage.expected)
    console.log(`Deploying project docker image:\n\t${deploy_link}`)
  } else {
    const {deploy_link} = await deployProjectDockerImage(dockerImage.expected)
    console.log(`Deploying project docker image:\n\t${deploy_link}`)
  }
}

async function handle() {
  const dockerImage = await statDockerImage()
  console.log('dockerImage:', dockerImage) // TODO: rm

  const {job_id, deploy_link} = await deployProjectBuildResource()
  console.log(`Deploying project build resource:\n\t${deploy_link}`)

  if (dockerImage.actual !== dockerImage.expected) {
    console.log(`Docker image should be updated:\n\t${dockerImage.actual} -> ${dockerImage.expected}`)
    const result = await waitJob(job_id, {maxAttempts: 180, delay: 10000})
    console.log('waitJob:', result) // TODO: type and rm

    const {deploy_link} = await deployProjectDockerImage(dockerImage.expected)
    console.log(`Deploying project docker image:\n\t${deploy_link}`)
  }
}

async function statDockerImage() {
  const serviceId = serviceYaml.getNannyServiceId(BUILD_RELEASE)
  const data = await getRuntimeAttrs({serviceId, token: NANNY_TOKEN})
  const actual = getByPath(data, ['content', 'instance_spec', 'dockerImage', 'name'])
  const expected = getProjectImageTag({projectName: PROJECT_NAME, appEnv: BUILD_RELEASE})

  return {actual, expected}
}

function deployProjectBuildResource() {
  return deploy({
    env: BUILD_RELEASE as DeployEnv,
    serviceName: SERVICE_NAME,
    token: CLOWNDUCTOR_TOKEN,
    sandboxResources: [
      {
        task_id: BUILD_TASK_ID,
        task_type: BUILD_TASK_TYPE,
        resource_id: BUILD_RESOURCE_ID,
        resource_type: BUILD_RESOURCE_TYPE,
        local_path: BUILD_RESOURCE_PATH,
      },
    ],
  })
}

function deployProjectDockerImage(dockerImage: string) {
  return deploy({
    env: BUILD_RELEASE as DeployEnv,
    serviceName: SERVICE_NAME,
    token: CLOWNDUCTOR_TOKEN,
    dockerImage,
  })
}
