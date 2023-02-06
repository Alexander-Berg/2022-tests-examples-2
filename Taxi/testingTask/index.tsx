import React, { useState } from 'react';

import Row from '../../../../components/row';
import { Task } from '../../../../types/models/Task';
import { ConfigurationTestRecord } from '../../../../types/models/ConfigurationTestRecord';
import getEmptyTestingAggregation, { TestingAggregation } from '../../../../types/models/TestingAggregation';
import { COUNT_RECORDS_PER_PAGE } from '../../../../redux/testings/sagas';
import TestingRecord from '../testingRecord';
import Column from '../../../../components/column';
import LoadingRow from '../../../../components/loadingRow';
import TestingAggregationComponent from '../testingAggregation';
import ConfigurableSelect, { SelectConfig } from '../../../../components/select/configurable';
import Container from '../../../../components/container';
import NoDataRow from '../../../../components/noDataRow';
import useEffectWithoutInitial from '../../../../hooks/useEffectWithoutInitial';
import i18n from '../../../../services/i18n';

import './styles.scss';
import { gaps } from '../../../../stylesConfig';

type TestingTaskProps = {
  value: Task,
  aggregation: TestingAggregation | null,
  aggregationLoading?: boolean,
  records: ConfigurationTestRecord[],
  recordsLoading?: boolean,
  recordsCount: number,
  onDownloadResultClick: (pageIndex: number, isEqual?: boolean) => void,
}

const equalSelectConfig: SelectConfig = {
  options: [
    { value: undefined, label: i18n.t("PAGE_TESTING.EQUALS.ALL") },
    { value: true, label: i18n.t("PAGE_TESTING.EQUALS.ONLY_MATCHED") },
    { value: false, label: i18n.t("PAGE_TESTING.EQUALS.ONLY_NOT_MATCHED") },
  ],
  labelFunction: (option) => option.label,
  valueFunction: (option) => option.value,
}

export default function TestingTask({
  value,
  records,
  aggregation = getEmptyTestingAggregation(),
  aggregationLoading = false,
  recordsLoading = false,
  recordsCount = 0,
  onDownloadResultClick,
}: TestingTaskProps) {
  const [activePage, setActivePage] = useState<number>(0);
  const [filterOnlyDiff, setFilterOnlyDiff] = useState<boolean | undefined>(undefined);

  const pages = new Array(Math.ceil(recordsCount / COUNT_RECORDS_PER_PAGE) || 0)
    .fill('')
    .map((page, index) => (
        <span
          key={index}
          className={`page ${index === activePage ? 'active' : ''}`}
          onClick={() => handleSetActivePage(index)}
        >
          {index + 1}
        </span>
      )
    );

  useEffectWithoutInitial(() => {
    onDownloadResultClick(activePage, filterOnlyDiff);
  }, [activePage, filterOnlyDiff])

  const handleSetActivePage = (index: number) => {
    if (!recordsLoading) {
      setActivePage(index);
    }
  }

  if (recordsLoading && aggregationLoading) {
    return <LoadingRow />;
  }

  const historyUsed = value.features && typeof value.features.use_history === 'boolean' && value.features.use_history;
  
  if (aggregation) {
    aggregation.samplingSize = recordsCount;
  }

  return (
    <Column autosize gap={gaps.formElements} className="records-list">
      {aggregationLoading ? (
        <LoadingRow />
      ) : (
        aggregation && <TestingAggregationComponent value={aggregation} />
      )}
      <Row autosize alignItems="center" justifyContent="space-between">
        <Row gap={4} flexWrap="wrap">{ pages }</Row>
        <Container width={240} flexShrink={0}>
          <ConfigurableSelect menuPortalTarget={document.body} config={equalSelectConfig} value={filterOnlyDiff} onChange={setFilterOnlyDiff} />
        </Container>
      </Row>
      {recordsLoading ? (
        <LoadingRow />
      ) : (
        records.length > 0 ? records.map((record) => (
          <TestingRecord key={record.id} record={record} historyUsed={historyUsed} />
        )) : (
          <NoDataRow />
        )
      )}
    </Column>
  )
}