import { objSnakeToCamel } from "../../services/helpers/utilities";
import { TestingAggregationBackend } from "../backendModels/TestingAggregationBackend";
import { TestingAggregation } from "../models/TestingAggregation";

export default function parseTestingAggregation(value: TestingAggregationBackend): TestingAggregation {
  return {
    ...objSnakeToCamel(value),
    topicDetails: JSON.parse(value.topic_details),
  }
}
