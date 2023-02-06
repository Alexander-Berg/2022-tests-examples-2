import {RequestStatusInitial} from 'consts';
import {BaseState} from 'utils/reducers/flow';
import {RequestStatus} from 'utils/reducers/flow/types';

export function getGeneratorMock<S>(data: S, status: RequestStatus = RequestStatusInitial): BaseState<S> {
    return {
        data: data,
        status: status,
        desc: null,
    };
};
