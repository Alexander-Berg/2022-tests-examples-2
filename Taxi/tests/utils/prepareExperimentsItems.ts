import {ResponseItem} from '@lavka/api-typings/schemas/exp3-matcher-sidecar/api'

export type Experiments = Record<string, Record<string, unknown>>

export const prepareExperimentsItems = (data: Experiments) => {
  const responseItems: ResponseItem[] = []

  Object.entries(data).forEach(([key, value]) => {
    responseItems.push({name: key, value})
  })

  return JSON.stringify(responseItems)
}
