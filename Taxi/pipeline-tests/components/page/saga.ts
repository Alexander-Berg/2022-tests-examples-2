import {all, call} from 'typed-redux-saga';

import {service as pipelineCommonService} from '../../../common/sagas/services/PipelineCommonService';
import {service as entityService} from '../../sagas/services/EntityService';
import {service as pipelineTestsService} from '../../sagas/services/PipelineTestsService';

export const saga = {
    onLoad: function* (serviceName: string) {
        yield* all([
            call(pipelineCommonService.run, serviceName),
            call(pipelineTestsService.run),
            call(entityService.run),
        ]);
    },
    onDispose: function* () {
        yield* all([
            call(pipelineCommonService.destroy),
            call(pipelineTestsService.destroy),
            call(entityService.destroy),
        ]);
    },
};
