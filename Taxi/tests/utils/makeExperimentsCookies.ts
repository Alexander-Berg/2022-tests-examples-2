import {Experiments, prepareExperimentsItems} from './prepareExperimentsItems'

interface Result {
  'experiments:items': string
}

export const makeExperimentsCookies = (data: Experiments): Result => {
  return {
    'experiments:items': prepareExperimentsItems(data),
  }
}
