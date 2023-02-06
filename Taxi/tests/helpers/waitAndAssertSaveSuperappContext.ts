import {TestDefinitionCallbackCtx} from 'hermione'

import {AssertClientRequestOptions, waitAndAssertClientRequest} from '@lavka/tests'

interface SuperappContextLavkaValues {
  tipsLastProposalAmount?: string
  tipsLastProposalAmountType?: string
  tipsRemember?: boolean
}

interface SuperappContextRequest {
  lavka: SuperappContextLavkaValues
}

type AssertOptions = Omit<AssertClientRequestOptions<{content: string | null}>, 'matchData'>

export const waitAndAssertSaveSuperappContext = async (
  ctx: TestDefinitionCallbackCtx,
  matchValues: SuperappContextLavkaValues,
  assertOptions: AssertOptions,
) => {
  await waitAndAssertClientRequest<{content: string | null}>(
    ctx,
    {forUrlLike: 'user/superapp-context', method: 'post'},
    {
      ...assertOptions,
      matchData: data => {
        const parsedData = data.content ? (JSON.parse(data.content) as SuperappContextRequest) : undefined
        if (!parsedData?.lavka) {
          return false
        }

        return (Object.keys(matchValues) as Array<keyof SuperappContextLavkaValues>).every(
          key => parsedData.lavka[key] === matchValues[key],
        )
      },
    },
  )
}
