import { SagaIterator } from "redux-saga";
import { call, fork, put, select, takeLatest } from "redux-saga/effects";
import apiService, { ApiResponse } from "../../services/api";
import { TaskType } from "../../types/models/Task";
import { parseTask } from "../../types/parsers/TaskParser";
import { parseConfigurationTestRecord } from "../../types/parsers/ConfigurationTestRecordParser";
import { GetConfigurationTestResultRequest, GetConfigurationTestResultResponse, GetTestingAggregationRequest, GetTestingAggregationResponse } from "../../types/requests/ConfigutationTest";
import { ProjectRequestParams } from "../../types/requests/Projects";
import { CreateTaskRequest, CreateTaskResponse, GetTasksRequest, GetTasksResponse } from "../../types/requests/Task";
import parseTestingAggregation from "../../types/parsers/TestingAggregationParser";
import { getGeneralRequestParams } from "../selectors";
import i18n from "../../services/i18n";

import * as actions from './actions';
import { ErrorAction } from "../reducers";

export const COUNT_RECORDS_PER_PAGE = 5;
export const TESTING_TASKS_CHUNK_SIZE = 10;

function* loadTestings(): SagaIterator {
  yield takeLatest(actions.loadTestings.request, function* (action) {
    try {
      const { olderThan, limit = TESTING_TASKS_CHUNK_SIZE } = action.payload;
      const params: GetTasksRequest = {
        types: [TaskType.testConfiguration],
        limit: TESTING_TASKS_CHUNK_SIZE,
        ...(olderThan && { older_than: olderThan }),
      }

      const response: ApiResponse<GetTasksResponse> = yield call(apiService.getTasks, params);

      const parsedTasks = response.data.tasks.map((bTask) => parseTask(bTask));
      yield put(actions.loadTestings.success({
        tasks: parsedTasks,
        pagination: {
          olderThan,
          limit,
        }
      }));
    } catch (err) {
      yield put(actions.loadTestings.failure(new ErrorAction(err, i18n.t("ERRORS.API.TESTINGS.LOAD"))));
    }
  })
}

function* createTesting() {
  yield takeLatest(actions.createTesting.request, function* (action) {
    try {
      const { samplingSlug, useHistory = false } = action.payload;
      const general: ProjectRequestParams = yield select(getGeneralRequestParams);
      const params: CreateTaskRequest = {
        ...general,
        type: TaskType.testConfiguration,
        params: {
          sample_slug: samplingSlug,
          use_history: useHistory,
        }
      }

      const response: ApiResponse<CreateTaskResponse> = yield call(apiService.createTask, params);

      const parsedTask = parseTask(response.data);
      yield put(actions.createTesting.success(parsedTask));
    } catch (err) {
      yield put(actions.createTesting.failure(new ErrorAction(err, i18n.t("ERRORS.API.TESTINGS.LAUNCH"))));
    }
  })
}

function* loadTestingResults() {
  yield takeLatest(actions.loadTestingResulsts.request, function* (action) {
    try {
      const { taskId, page, isEqual } = action.payload;
      const params: GetConfigurationTestResultRequest = {
        task_id: taskId,
        limit: COUNT_RECORDS_PER_PAGE,
        offset: page * COUNT_RECORDS_PER_PAGE,
        is_equal: isEqual,
      }

      const response: ApiResponse<GetConfigurationTestResultResponse> = yield call(apiService.getTestingResults, params);
      const parsedRecords = response.data.test_records.map((record) => parseConfigurationTestRecord(record));
      const total = response.data.total_records;
      yield put(actions.loadTestingResulsts.success({ taskId, page, records: parsedRecords, total }));
    } catch (err) {
      yield put(actions.loadTestingResulsts.failure(new ErrorAction(
        err,
        i18n.t("ERRORS.API.TESTINGS.TESTING_RESULTS_LOAD"),
        { taskId: action.payload.taskId }
      )))
    }
  })
}

function* loadTestingAggregation(): SagaIterator {
  yield takeLatest(actions.loadTestingAggregation.request, function* (action) {
    const { taskId } = action.payload;
    try {
      const general: ProjectRequestParams = yield select(getGeneralRequestParams);
      const params: GetTestingAggregationRequest = {
        ...general,
        task_id: taskId,
      }

      const response: ApiResponse<GetTestingAggregationResponse> = yield call(apiService.getTestingAggregation, params);

      if (response.status === 204) {
        yield put(actions.loadTestingAggregation.success({ taskId, result: null }));
      } else {
        const parsedTestingAggregation = parseTestingAggregation(response.data);
        yield put(actions.loadTestingAggregation.success({ taskId, result: parsedTestingAggregation })); 
      }
    } catch (err) {
      yield put(actions.loadTestingAggregation.failure(new ErrorAction(
        err,
        i18n.t("ERRORS.API.TESTINGS.AGREGATED_RESULTS_LOAD"), 
        { taskId }
      )));
    }
  })
}

export default function* testingsSagas(): SagaIterator {
  yield fork(loadTestings);
  yield fork(createTesting);
  yield fork(loadTestingResults);
  yield fork(loadTestingAggregation);
}
