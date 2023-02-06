import {getWebpackBuildResult} from '../build'

describe('webpack tree shaking', () => {
  it.skip('geo-client', async () => {
    const result = await getWebpackBuildResult('geo-client')

    expect(result).toContain(`"/persuggest/v1/zerosuggest"`)
    expect(result).not.toContain(`"/persuggest/v1/finalsuggest"`)
  })
})
