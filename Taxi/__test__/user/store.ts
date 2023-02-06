import {RequestStatusSuccessful} from 'consts';
import {SelectorTestDataType} from 'types/tests';
import {getGeneratorMock} from 'utils/tests/getGeneratorMock';
import {getStoreByPart} from 'utils/tests/getPartOfStore';

const INITIAL_USER_DATA: GlobalStateType['app']['user']['data'] = {
    permissions: [],
    evaluated_permissions: [],
    restrictions: [],
};
const FULLFILLED_USER_DATA: GlobalStateType['app']['user']['data'] = {
    permissions: [
        'add_delete_subcluster_on_metaqueue',
        'edit_metaqueue_state',
        'edit_subcluster_state',
        'manage_exams',
        'list_operators',
        'make_outgoing_calls',
        'receive_calls',
        'search_operators',
        'set_operators_queues',
        'view_single_call',
        'create_support_ticket',
        'view_calls',
        'view_subcluster_statistics',
        'cancel_taxi_order',
        'create_taxi_order',
        'estimate_taxi_order',
        'list_taxi_orders',
        'create_taxi_order_without_call',
    ],
    evaluated_permissions: [],
    restrictions: [],
};

export const getAccessRestrictedMockInitial = () => {
    const data: SelectorTestDataType<boolean> = {
        store: getStoreByPart('app.user', getGeneratorMock(INITIAL_USER_DATA)),
        result: true,
    };

    return data;
};
export const getAccessRestrictedMockSuccess = () => {
    const data: SelectorTestDataType<boolean> = {
        store: getStoreByPart('app.user', getGeneratorMock(FULLFILLED_USER_DATA)),
        result: false,
    };

    return data;
};

export const getUserDomainsMock = () => {
    const data: SelectorTestDataType<string[]> = {
        store: getStoreByPart('app.user', getGeneratorMock(FULLFILLED_USER_DATA)),
        result: [],
    };

    return data;
};

export const getUserStatusMock = () => {
    const data: SelectorTestDataType<string> = {
        store: getStoreByPart('app.user', getGeneratorMock(FULLFILLED_USER_DATA, RequestStatusSuccessful)),
        result: RequestStatusSuccessful,
    };

    return data;
};
