import type {TestDefinitionCallbackCtx} from 'hermione'

interface Params {
  categoryId: string
  groupId?: string
}

export async function openCategoryPage(ctx: TestDefinitionCallbackCtx, params: Params) {
  const groupId = params.groupId ?? 'UNKNOWN_GROUP_ID'

  await ctx.browser.openPage(`/?group=${groupId}&category=${params.categoryId}`)
}
