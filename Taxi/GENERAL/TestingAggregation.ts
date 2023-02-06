export type TestingAggregation = {
  samplingSize: number,
  equalsPercent: number,
  topicAccuracyV1: number,
  topicAccuracyV2: number,
  replyPercentV1: number,
  replyPercentV2: number,
  closePercentV1: number,
  closePercentV2: number,
  replyOrCloseV1: number,
  replyOrCloseV2: number,
  topicDetails: { [topicSlug: string]: { v1: number, v2: number, IOU: number } },
};

export default function getEmptyTestingAggregation(): TestingAggregation {
  return {
    samplingSize: 0,
    equalsPercent: 0,
    topicAccuracyV1: 0,
    topicAccuracyV2: 0,
    replyPercentV1: 0,
    replyPercentV2: 0,
    closePercentV1: 0,
    closePercentV2: 0,
    replyOrCloseV1: 0,
    replyOrCloseV2: 0,
    topicDetails: {},
  }
}