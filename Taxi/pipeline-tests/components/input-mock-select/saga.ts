import {call} from 'typed-redux-saga';

import {apiInstance as mocksAPI} from '../../../common/api/MocksAPI';
import {getCurrentServiceName} from '../../../common/utils';

export const saga = {
    onLoad: function* () {
        return yield* call(mocksAPI.request, getCurrentServiceName());
    },
};
