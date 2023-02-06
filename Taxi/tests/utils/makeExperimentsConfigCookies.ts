import {Experiments, prepareExperimentsItems} from './prepareExperimentsItems'

interface Result {
  'experimentsConfig:items': string
}

export const makeExperimentsConfigCookies = (data: Experiments): Result => {
  return {
    'experimentsConfig:items': prepareExperimentsItems(data),
  }
}
