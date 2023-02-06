import execa from 'execa'
import fs from 'fs-extra'
import {nanoid} from 'nanoid'

export const createPullRequest = () => {
  const uniqId = nanoid()
  const branchId = `arc-load-testing-${uniqId}`

  execa.sync('arc', ['checkout', 'trunk'])
  execa.sync('arc', ['checkout', '-b', branchId])
  fs.outputFileSync('projects/website/arc-load-testing', `hello!, ${branchId}`)
  execa.sync('arc', ['add', '.'])
  execa.sync('arc', ['commit', '-a', '-m', `"load testing ${branchId}"`])
  execa.sync('arc', ['pr', 'create', '--push', '--no-edit', '--publish'])

  return branchId
}

export const createPullRequests = (count: number, resultFile: string) => {
  const branchIds = []
  for (let i = 0; i < count; i++) {
    branchIds.push(createPullRequest())
  }

  fs.outputJsonSync(resultFile, branchIds)
}
