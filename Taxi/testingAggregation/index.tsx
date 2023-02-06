import React from 'react';
import { useTranslation } from 'react-i18next';

import Column from '../../../../components/column';
import Text from '../../../../components/text';
import Row from '../../../../components/row';
import getEmptyTestingAggregation, { TestingAggregation } from '../../../../types/models/TestingAggregation';
import FoldedList from '../../../../components/foldedList';

import { gaps } from '../../../../stylesConfig';
import './styles.scss';

type TestingAggregationProps = {
  value: TestingAggregation,
  historyUsed?: boolean,
}

export default function ({
  value = getEmptyTestingAggregation(),
  historyUsed = false,
}: TestingAggregationProps) {
  const { t } = useTranslation();
  return (
    <Column autosize gap={gaps.base} className="testing-aggregation">
      <Row className="main-row" autosize gap={gaps.big}>
        <Text fontSize={18}>{t("PAGE_TESTING.SAMPLING_SIZE")}: {value.samplingSize}</Text>
        <Text fontSize={18}>{t("PAGE_TESTING.MATCH_PERCENT")}: {value.equalsPercent || 0}%</Text>
      </Row>
      <div style={{ width: '100%' }}>
        <div className="aggregated-row">
          <Text></Text>
          <Text bold>{historyUsed ? t("PAGE_TESTING.HISTORICAL_ANSWER") : t("PAGE_TESTING.DRAFT")}</Text>
          <Text bold>Release</Text>
          <Text bold>IOU</Text>
        </div>
        <div className="aggregated-row">
          <Text>{t("PAGE_TESTING.TOPIC_PRECISION")}</Text>
          <Text>{value.topicAccuracyV1}%</Text>
          <Text>{value.topicAccuracyV2}%</Text>
        </div>
        <div className="aggregated-row">
          <Text>{t("PAGE_TESTING.ANSWERS_PERCENT")}</Text>
          <Text>{value.replyPercentV1}%</Text>
          <Text>{value.replyPercentV2}%</Text>
        </div>
        <div className="aggregated-row">
          <Text>{t("PAGE_TESTING.CLOSING_PERCENTAGE")}</Text>
          <Text>{value.closePercentV1}%</Text>
          <Text>{value.closePercentV2}%</Text>
        </div>
        <div className="aggregated-row">
          <Text>{t("PAGE_TESTING.AUTOMATIZATION_PERCENTAGE")}</Text>
          <Text>{value.replyOrCloseV1}%</Text>
          <Text>{value.replyOrCloseV2}%</Text>
        </div>
      </div>
      <FoldedList className="topic-list" size={3} gap={0}>
        {Object.keys(value.topicDetails).map((topicSlug) => (
          <div key={topicSlug} style={{ width: '100%' }} className="aggregated-row">
            <Text className="crop-text">{topicSlug}</Text>
            <Text>{value.topicDetails[topicSlug].v1}</Text>
            <Text>{value.topicDetails[topicSlug].v2}</Text>
            <Text>{value.topicDetails[topicSlug].IOU}%</Text>
          </div>
        ))}
      </FoldedList>
    </Column>
  )
}