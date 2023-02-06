import { ConfigurationTestRecord } from "../../types/models/ConfigurationTestRecord";
import { AppState } from "../reducers";

export const getConfigurationTestResults = (state: AppState): { [taskId: string]: { page: number, loading: boolean, records: ConfigurationTestRecord[], total: number } } => {
  const { list: tasks, results } = { ...state.testings };

  return tasks.value.reduce<{ [taskId: string]: { page: number, loading: boolean, records: ConfigurationTestRecord[], total: number } }>((obj, task) => {
    if (results[task.id]) {
      obj[task.id] = results[task.id];
    } else {
      obj[task.id] = {
        loading: false,
        page: -1,
        records: [],
        total: 0,
      }
    }

    return obj;
  }, {});
} 