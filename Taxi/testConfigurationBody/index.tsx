import React from 'react';
import { connect } from 'react-redux';

import { AppState } from '../../../redux/reducers';
import { Sampling } from '../../../types/models/Sampling';
import { Task, TaskType } from '../../../types/models/Task';
import Column from '../../column';
import Row from '../../row';
import Text from '../../text';
import AuthorLabel from '../authorLabel';
import { FileLabel } from '../fileLabel';
import TaskMessage from '../taskMessage';
import TaskTypeComponent from '../taskType';

type BaseTaskBodyProps = {
  task: Task,
  onFileDownloadClick?: (fileId: string) => void,
}

function TestConfigurationTaskBody({
  task,
  samplings,
  onFileDownloadClick,
}: BaseTaskBodyProps & ReduxProps) {
  let samplingsLabel = task.features ? task.features.sample_slug : '';

  const samplingIndex = samplings.value.findIndex((sampling) => sampling.slug === samplingsLabel);
  if (samplingIndex !== -1) {
    samplingsLabel = samplings.value[samplingIndex].name;
  }

  return (
    <Column>
      <Row gap={5}>
        <TaskTypeComponent type={task.type} />
        {task.type === TaskType.testConfiguration && task.features && (
          <span style={{ wordBreak: 'break-all' }}>
            <Text>{samplingsLabel} </Text>
            {task.features.records_count && <Text title="Размер выборки">({task.features.records_count})</Text>}
          </span>
        )}
        {task.errorMessage && <TaskMessage message={task.errorMessage} />}
        {task.fileId && onFileDownloadClick && <FileLabel fileId={task.fileId} onClick={onFileDownloadClick} />}
      </Row>
      {task.user && (
        <Row>
          <AuthorLabel login={task.user.login} />
        </Row>
      )}
    </Column>
  )
}

type MapStateToProps = {
  samplings: {
    value: Sampling[],
    loading: boolean,
  }
}

const mapStateToProps = (state: AppState): MapStateToProps => ({
  samplings: state.samplings.list
});

type ReduxProps = MapStateToProps;

export default connect(mapStateToProps, {})(TestConfigurationTaskBody);