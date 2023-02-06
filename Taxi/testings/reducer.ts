import { Reducer } from 'redux';
import { ActionType, createReducer } from "typesafe-actions";

import { ConfigurationTestRecord } from '../../types/models/ConfigurationTestRecord';
import { Task } from "../../types/models/Task";
import getEmptyTestingAggregation, { TestingAggregation } from '../../types/models/TestingAggregation';
import { isLastChunk } from '../tasks/reducer';

import * as actions from './actions';
import * as projectsActions from '../projects/actions';

type TestingsState = {
  list: {
    value: Task[],
    loading: boolean,
    total: number,
  },
  results: {
    [taskId: string]: {
      page: number,
      loading: boolean,
      records: ConfigurationTestRecord[],
      total: number,
    },
  },
  aggregations: {
    [taskId: string]: {
      value: TestingAggregation | null,
      loading: boolean,
    }
  }
}

const initialState: TestingsState = {
  list: {
    value: [],
    loading: false,
    total: 0,
  },
  results: {},
  aggregations: {},
}

export const testingsReducer: Reducer<TestingsState> = createReducer<TestingsState>(initialState)
  .handleAction(
    actions.loadTestings.request,
    (state: TestingsState, { payload: pagination }: ActionType<typeof actions.loadTestings.request>): TestingsState => ({
      ...state,
      list: {
        ...state.list,
        loading: true,
        total: pagination.olderThan ? state.list.total : 0,
      }
    })
  )
  .handleAction(
    actions.loadTestings.success,
    (state: TestingsState, { payload: { tasks, pagination } }: ActionType<typeof actions.loadTestings.success>): TestingsState => {
      const currentTasks = pagination?.olderThan ? state.list.value.concat(tasks) : tasks;
      const sortedTasks = currentTasks.sort((taskA, taskB) => +(new Date(taskB.created)) - +(new Date(taskA.created)));
      const noMoreTasks = isLastChunk(pagination, tasks);
      return {
        ...state,
        list: {
          ...state.list,
          value: sortedTasks,
          loading: false,
          total: noMoreTasks ? sortedTasks.length : state.list.total,
        }
      }
    }
  )
  .handleAction(
    actions.loadTestings.failure,
    (state: TestingsState): TestingsState => ({
      ...state,
      list: {
        ...state.list,
        loading: false,
      }
    })
  )
  .handleAction(
    actions.createTesting.request,
    (state: TestingsState): TestingsState => ({
      ...state,
      list: {
        ...state.list,
        loading: true,
      }
    })
  )
  .handleAction(
    actions.createTesting.success,
    (state: TestingsState, { payload }: ActionType<typeof actions.createTesting.success>): TestingsState => ({
      ...state,
      list: {
        ...state.list,
        value: [payload, ...state.list.value],
        loading: false,
      }
    })
  )
  .handleAction(
    actions.createTesting.failure,
    (state: TestingsState): TestingsState => ({
      ...state,
      list: {
        ...state.list,
        loading: false,
      }
    })
  )
  .handleAction(
    actions.loadTestingResulsts.request,
    (state: TestingsState, { payload }: ActionType<typeof actions.loadTestingResulsts.request>): TestingsState => {
      const { taskId, page } = payload;
      const results = { ...state.results };

      if (!results[taskId]) {
        results[taskId] = {
          page,
          records: [],
          loading: true,
          total: 0,
        }
      } else {
        results[taskId] = {
          ...results[taskId],
          loading: true,
        }
      }

      return {
        ...state,
        results,
      }
    }
  )
  .handleAction(
    actions.loadTestingResulsts.success,
    (state: TestingsState, { payload }: ActionType<typeof actions.loadTestingResulsts.success>): TestingsState => {
      const { taskId, records, page, total } = payload;
      const results = { ...state.results };

      if (!results[taskId]) {
        results[taskId] = {
          page,
          records,
          loading: false,
          total: 0,
        }
      } else {
        results[taskId].records = records;
        results[taskId].loading = false;
        results[taskId].total = total;
      }

      return {
        ...state,
        results,
      }
    }
  )
  .handleAction(
    actions.loadTestingResulsts.failure,
    (state: TestingsState, { payload: error }: ActionType<typeof actions.loadTestingResulsts.failure>): TestingsState => {
      const { taskId } = error.payload;
      const results = { ...state.results };

      if (!results[taskId]) {
        results[taskId] = {
          page: -1,
          records: [],
          loading: false,
          total: 0,
        }
      } else {
        results[taskId].loading = false;
      }

      return {
        ...state,
        results,
      }
    }
  )
  .handleAction(
    actions.loadTestingAggregation.request,
    (state: TestingsState, { payload: { taskId } }: ActionType<typeof actions.loadTestingAggregation.request>): TestingsState => {
      return updateTestingAggregation(state, taskId, () => ({ value: getEmptyTestingAggregation(  ), loading: true }));
    } 
  )
  .handleAction(
    actions.loadTestingAggregation.success,
    (state: TestingsState, { payload: { taskId, result } }: ActionType<typeof actions.loadTestingAggregation.success>): TestingsState => {
      return updateTestingAggregation(state, taskId, () => ({ value: result, loading: false }));
    }
  )
  .handleAction(
    actions.loadTestingAggregation.failure,
    (state:TestingsState, { payload: { payload: { taskId } } }: ActionType<typeof actions.loadTestingAggregation.failure>): TestingsState => {
      return updateTestingAggregation(state, taskId, (result) => ({ value: null, loading: false }));
    }
  )
  .handleAction(
    projectsActions.selectProject,
    (state: TestingsState): TestingsState => ({
      ...state,
      list: {
        ...state.list,
        value: [],
      }
    })
  )
  
function updateTestingAggregation(state: TestingsState, taskId: string, callback: (value: TestingAggregation) => { value: TestingAggregation | null, loading: boolean }): TestingsState {
  const resultExists = !!state.aggregations[taskId];

  if (resultExists) {
    return {
      ...state,
      aggregations: {
        ...state.aggregations,
        [taskId]: callback((state.aggregations[taskId].value as TestingAggregation)),
      }
    }
  } else {
    const newResult = getEmptyTestingAggregation();
    return {
      ...state,
      aggregations: {
        ...state.aggregations,
        [taskId]: callback(newResult),
      }
    }
  }
}