import {call} from 'typed-redux-saga';

import {apiInstance as checksAPI} from '../../../common/api/ChecksAPI';
import {getCurrentServiceName} from '../../../common/utils';

export const saga = {
    onLoad: function* () {
        return yield* call(checksAPI.request, getCurrentServiceName());
    },
};
