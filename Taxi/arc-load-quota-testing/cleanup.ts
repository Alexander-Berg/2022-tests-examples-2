import execa from 'execa'
import fs from 'fs-extra'

export const cleanupPullRequests = (resultFile: string) => {
  const branchIds = fs.readJSONSync(resultFile)
  const username = execa.sync('whoami').stdout

  execa.sync('arc', ['checkout', 'trunk'])

  for (const branchId of branchIds) {
    const remoteBranchId = `users/${username}/${branchId}`

    console.log(`remove branch ${remoteBranchId}`)
    execa.sync('arc', ['push', '-d', remoteBranchId])
    execa.sync('arc', ['branch', '-D', branchId])
  }
}
