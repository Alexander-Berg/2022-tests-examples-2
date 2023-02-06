import {expect} from 'chai'
import {TestDefinitionCallbackCtx} from 'hermione'

import {ONE_FIFTH_A_SECOND} from '@lavka/constants'
import {RequestStackItem} from '@lavka/utils'

import {invariant} from '../utils'

export interface AssertClientRequestOptions<MatchData> {
  matchDeepInclude?: Record<string, unknown>
  haveBeenCalledTimes?: number
  matchData?: (data: MatchData) => boolean
  calledAfter?: [string, {haveBeenCalledTimes: number; method?: string}]
}

const WAITING_TIMEOUT_MS = 10000

interface Options {
  forUrlLike: string
  method: string
}

export type ForUrlLikeOrOptionsType = Options | string

/* Выполняет поиск запроса c forUrlLike в стеке клиентских запросов.
   Есть возможность уточнить какой именно запрос нужно искать при помощи options.
   Есть возможность убедиться, что запрос X был вызван до запроса Y при помощи calledAfter
* */
export const waitAndAssertClientRequest = async <MatchData = unknown>(
  ctx: TestDefinitionCallbackCtx,
  forUrlLikeOrOptions: ForUrlLikeOrOptionsType,
  options: AssertClientRequestOptions<MatchData>,
  remainingTimeout = WAITING_TIMEOUT_MS,
) => {
  const {matchDeepInclude, haveBeenCalledTimes, matchData} = options

  const beforeCalledUrl = options?.calledAfter?.[0]
  const beforeCalledOptions = options?.calledAfter?.[1]

  let forUrlLike = typeof forUrlLikeOrOptions === 'string' ? forUrlLikeOrOptions : undefined
  let method: string | undefined = undefined

  if (!forUrlLike && typeof forUrlLikeOrOptions === 'object') {
    forUrlLike = forUrlLikeOrOptions.forUrlLike
    method = forUrlLikeOrOptions.method
  }
  invariant(forUrlLike)

  const {foundElem, isValidBeforeRequest} = await ctx.browser.execute(
    ({forUrlLike, method, beforeUrl, beforeOptions}) => {
      const stack = window.requestsStack
      if (!stack || !window.requestsStack) {
        throw new Error('no requestsStack found in window')
      }

      const currentStack = window.requestsStack
      let foundElem: typeof window.requestsStack[number] | undefined = undefined
      let isValidBeforeRequest = !beforeUrl

      for (let i = currentStack.length; i--; i >= 0) {
        const elem = currentStack[i]

        if (!foundElem && elem.url?.includes(forUrlLike) && (!method || method === elem.method)) {
          foundElem = elem
          continue
        }
        if (foundElem && beforeUrl && beforeOptions) {
          if (
            elem.url?.includes(beforeUrl) &&
            beforeOptions?.haveBeenCalledTimes === elem.calledCount &&
            (!beforeOptions.method || beforeOptions.method === elem.method)
          ) {
            isValidBeforeRequest = true
          }
        }
      }

      return {foundElem, isValidBeforeRequest}
    },
    {forUrlLike, method, beforeUrl: beforeCalledUrl, beforeOptions: beforeCalledOptions},
  )

  if (!foundElem && remainingTimeout > 0) {
    await ctx.browser.pause(ONE_FIFTH_A_SECOND)
    await waitAndAssertClientRequest(ctx, forUrlLikeOrOptions, options, remainingTimeout - ONE_FIFTH_A_SECOND)
    return
  }

  if (!foundElem) {
    throw new Error(
      `Not found client request for url/options "${forUrlLikeOrOptions}" with options: "${JSON.stringify(
        options,
      )}" after ${remainingTimeout}ms`,
    )
  }
  if (!isValidBeforeRequest) {
    throw new Error(
      `Failed checking for url sequence. The url/options "${forUrlLikeOrOptions}" is not following after url "${beforeCalledUrl}" with options "${JSON.stringify(
        beforeCalledOptions,
      )}" after ${remainingTimeout}ms`,
    )
  }

  if (matchData) {
    const isMatched = matchData(foundElem.data as MatchData)
    if (!isMatched) {
      throw new Error(`matchData returned false for stack item data: ${JSON.stringify(foundElem.data)}`)
    }
  }
  if (haveBeenCalledTimes) {
    expect(foundElem.calledCount).to.equals(haveBeenCalledTimes)
  }
  if (matchDeepInclude) {
    expect(foundElem.data).to.deep.include(matchDeepInclude)
  }
}

// TODO убрать дублирование с packages/utils/tests/createRecordRequestsInterceptor.ts
declare global {
  interface Window {
    requestsStack?: Array<RequestStackItem>
  }
}
