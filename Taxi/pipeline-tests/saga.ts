import {call} from 'typed-redux-saga';

import PipelineService from '../../sagas/services/PipelineService';

export const saga = {
    onLoad: function* () {
        yield* call(PipelineService.loadPipelineTestModel);
    },
};
