import React, { useState, useEffect } from 'react';
import { connect } from 'react-redux';
import { useTranslation } from 'react-i18next';

import Column from '../../components/column';
import Page from '../../components/page';
import PageHeader from '../../components/pageHeader';
import PageTitle from '../../components/pageTitle';
import Button from '../../components/button';
import Text from '../../components/text';
import TaskComponent from '../../components/taskComponents/task';
import SamplingSelector from '../../components/samplingSelector/fromDictionary';
import Row from '../../components/row';
import { AppState } from '../../redux/reducers';
import stylesConfig, { gaps } from '../../stylesConfig';
import { Sampling } from '../../types/models/Sampling';
import { Task } from '../../types/models/Task';
import Container from '../../components/container';

import * as actions from '../../redux/testings/actions';
import TestingTask from './components/testingTask';
import { Project } from '../../types/models/Project';
import RefreshButton from '../../components/button/refresh';
import { ConfigurationTestRecord } from '../../types/models/ConfigurationTestRecord';
import { getConfigurationTestResults } from '../../redux/testings/selectors';
import Icon from '../../components/icon';
import LazyLoadingList from '../../components/lazyLoadingList';
import modalService from '../../services/modal';
import { TestingAggregation } from '../../types/models/TestingAggregation';

export const POLLING_INTERVAL = 5000;

function PageTesting({
  testings,
  results,
  aggregations,
  selectedProject,
  loadTestings,
  loadTestingResults,
  loadTestingAggregation,
  createTesting,
}: ReduxProps) {
  const { t } = useTranslation();
  const [sampling, setSampling] = useState<Sampling | null>(null);
  const [showExtraLoading, setShowExtraLoading] = useState<boolean>(false); 

  useEffect(() => {
    loadTestings({});
    setSampling(null);
  }, [selectedProject]);

  useEffect(() => {
    if (!testings.loading) {
      setShowExtraLoading(false);
    }
  }, [testings.loading])

  const handleLaunchTestsClick = () => {
    
    if (sampling) {
      modalService.openLaunchTests({
        sampling,
        onSubmit: (useHistory) => {
          createTesting({
            samplingSlug: sampling.slug,
            useHistory,
          })
        },
      })
    }
  }

  const handleRefreshClick = () => {
    setShowExtraLoading(true);
    loadTestings({});
  }

  const handleExpandClick = (task: Task) => {
    if (results[task.id].records.length === 0) {
      loadTestingResults({ taskId: task.id, page: 0 });
    }
    if (!aggregations[task.id]) {
      loadTestingAggregation({ taskId: task.id });
    }
  }

  const loadMoreTasks = () => {
    const last = testings.value[testings.value.length - 1];
    if (last) {
      loadTestings({
        olderThan: +new Date(last.created),
      })
    }
  }

  const validateRunTests = () => {
    let status = true;
    let error: string | undefined = undefined;

    if (!sampling) {
      status = false;
      error = t("PAGE_TESTING.CHOOSE_SAMPLING");
    } else if (sampling.quantity === 0) {
      status = false;
      error = t("PAGE_TESTING.QUANTITY_INVALID");
    }

    return {
      status,
      error
    }
  }

  const canRunTests = validateRunTests();
  return (
    <Page>
      <PageHeader>
        <PageTitle>{t("PAGE_TESTING.TITLE")}</PageTitle>
      </PageHeader>
      <Column autosize gap={10}>
        <Row autosize gap={gaps.base}>
          <Container width={300} height={stylesConfig.baseFormItemHeight}>
            <SamplingSelector value={sampling} onChange={setSampling} />
          </Container>
          <Container width={150} height={stylesConfig.baseFormItemHeight}>
            <Button disabled={!canRunTests.status} title={canRunTests.error} type="button" onClick={handleLaunchTestsClick}>
              <Text>{t("PAGE_TESTING.LAUNCH_TESTS")}</Text>
            </Button>
          </Container>
          <Container flexGrow={1} height={stylesConfig.baseFormItemHeight}>
            <Row autosize justifyContent="flex-end" alignItems="center">
              { testings.loading && showExtraLoading && <Icon width={30} height={30} type="loading" /> }
            </Row>
          </Container>
          <RefreshButton onClick={handleRefreshClick}/>
        </Row>
        <LazyLoadingList
          onEndReached={loadMoreTasks}
          loading={testings.loading}
          total={testings.total}
          gap={1}
        >
          {testings.value.map((testing) => (
            <TaskComponent
              key={testing.id}
              task={testing}
              ExpandContent={() => (
                <div style={{padding: 10}}>
                  <TestingTask
                    value={testing}
                    aggregation={aggregations[testing.id].value}
                    aggregationLoading={aggregations[testing.id].loading}
                    recordsLoading={results[testing.id].loading}
                    records={results[testing.id].records}
                    recordsCount={results[testing.id].total}
                    onDownloadResultClick={(pageIndex, isEqual) => loadTestingResults({ taskId: testing.id, page: pageIndex, isEqual })}
                  />
                </div>
              )}
              onExpandClick={handleExpandClick}
            />
          ))}
        </LazyLoadingList>
      </Column>
    </Page>
  )
}

type MapStateToProps = {
  testings: {
    value: Task[]
    loading: boolean,
    total: number,
  },
  results: { [taskId: string]: { page: number, loading: boolean, records: ConfigurationTestRecord[], total: number } },
  aggregations: { [taskId: string]: {
      value: TestingAggregation | null,
      loading: boolean,
    },
  },
  selectedProject: Project,
}

const mapStateToProps = (state: AppState): MapStateToProps => ({
  testings: state.testings.list,
  results: getConfigurationTestResults(state),
  aggregations: state.testings.aggregations,
  selectedProject: state.projects.selectedProject,
})

type MapDisaptchToProps = {
  loadTestings: typeof actions.loadTestings.request,
  loadTestingResults: typeof actions.loadTestingResulsts.request,
  loadTestingAggregation: typeof actions.loadTestingAggregation.request,
  createTesting: typeof actions.createTesting.request,
}

const mapDispatchToProps: MapDisaptchToProps = {
  loadTestings: actions.loadTestings.request,
  loadTestingResults: actions.loadTestingResulsts.request,
  loadTestingAggregation: actions.loadTestingAggregation.request,
  createTesting: actions.createTesting.request,
};

type ReduxProps = MapStateToProps & MapDisaptchToProps;

export default connect(mapStateToProps, mapDispatchToProps)(PageTesting);