import execa from 'execa'
import fs from 'fs-extra'
import {nanoid} from 'nanoid'

const updatePullRequest = (branchId: string) => {
  const randomId = nanoid()
  execa.sync('arc', ['checkout', branchId])
  fs.outputFileSync('projects/website/arc-load-testing', `hello!, ${randomId}`)
  execa.sync('arc', ['commit', '-a', '-m', `"load testing ${branchId} ${randomId}"`])
  execa.sync('arc', ['push'])
}

const updatePullRequestsRaw = (branchIds: string[]) => {
  for (const branchId of branchIds) {
    updatePullRequest(branchId)
  }
}

export const updatePullRequests = (updateInterval: number, resultFile: string) => {
  const branchIds = fs.readJSONSync(resultFile)
  updatePullRequestsRaw(branchIds)

  setInterval(updatePullRequestsRaw.bind(null, branchIds), updateInterval)
}
