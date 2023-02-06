import {call} from 'typed-redux-saga';

import {TabType} from '../../enums';
import PipelineTestsService from '../../sagas/services/PipelineTestsService';

export const saga = {
    onLoad: function* (service: string, tabType: TabType) {
        yield* call(PipelineTestsService.loadEntityList, service, tabType);
    },
};
