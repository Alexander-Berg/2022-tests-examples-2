import { createAsyncAction } from "typesafe-actions";
import { Task } from "../../types/models/Task";
import { ConfigurationTestRecord } from "../../types/models/ConfigurationTestRecord";
import { Pagination } from "../../types/models/Pagination";
import { TestingAggregation } from "../../types/models/TestingAggregation";
import { ErrorAction } from "../reducers";

export const loadTestings = createAsyncAction(
  'testings/load/requested',
  'testings/load/succeeded',
  'testings/load/failed',
)<Pagination, { tasks: Task[], pagination?: Pagination }, ErrorAction>();

export const createTesting = createAsyncAction(
  'testings/create/requested',
  'testings/create/succeeded',
  'testings/create/failed',
)<{ samplingSlug: string, useHistory?: boolean }, Task, ErrorAction>();

export const loadTestingResulsts = createAsyncAction(
  'testingResult/load/requested',
  'testingResult/load/succeeded',
  'testingResult/load/failed',
)<{ taskId: string, page: number, isEqual?: boolean }, { taskId: string, page: number, records: ConfigurationTestRecord[], total: number } , ErrorAction<{ taskId: string }>>();

export const loadTestingAggregation = createAsyncAction(
  'testings/loadAggregation/requested',
  'testings/loadAggregation/succeeded',
  'testings/loadAggregation/failed',
)<{ taskId: string }, { taskId: string, result: TestingAggregation | null }, ErrorAction<{ taskId: string }>>();
