import {getSelectedOrderOrTaskMetadata} from '../sip';
import {EVENT_TYPE} from '../../consts';

const PARAM = 'PARAM';
const PARAM_TASK = 'PARAM_TASK';
const PARAM_ORDER_1 = 'PARAM_ORDER_1';
const PARAM_ORDER_2 = 'PARAM_ORDER_2';

const PARAM_UNCHANGED_TASK = 'PARAM_UNCHANGED_TASK';
const PARAM_UNCHANGED_ORDER_1 = 'PARAM_UNCHANGED_ORDER_1';
const PARAM_UNCHANGED_ORDER_2 = 'PARAM_UNCHANGED_ORDER_2';

const ORDER_TASK = 'ORDER_TASK';
const ORDER_1 = 'ORDER_1';
const ORDER_2 = 'ORDER_2';

describe('services/tasks/selectors/sip', () => {
    describe('getSelectedOrderOrTaskMetadata', () => {
        test('must return metadata of selected order', () => {
            expect(
                getSelectedOrderOrTaskMetadata({
                    selectedOrder: ORDER_2,
                    data: {
                        meta_info: {
                            order_id: ORDER_TASK,
                            [PARAM]: PARAM_TASK,
                            [PARAM_UNCHANGED_TASK]: PARAM_UNCHANGED_TASK
                        },
                        $view: {
                            unfilteredEvents: [
                                {
                                    type: EVENT_TYPE.MESSAGE,
                                    data: {
                                        metadata: {
                                            order_id: ORDER_1,
                                            [PARAM]: PARAM_ORDER_1,
                                            [PARAM_UNCHANGED_ORDER_1]: PARAM_UNCHANGED_ORDER_1
                                        }
                                    }
                                },
                                {
                                    type: EVENT_TYPE.MESSAGE,
                                    data: {
                                        metadata: {}
                                    }
                                },
                                {
                                    type: EVENT_TYPE.MESSAGE,
                                    data: {
                                        metadata: {
                                            order_id: ORDER_2,
                                            [PARAM]: PARAM_ORDER_2,
                                            [PARAM_UNCHANGED_ORDER_2]: PARAM_UNCHANGED_ORDER_2
                                        }
                                    }
                                }
                            ]
                        }
                    }
                })
            ).toEqual({
                order_id: ORDER_2,
                [PARAM]: PARAM_ORDER_2,
                [PARAM_UNCHANGED_TASK]: PARAM_UNCHANGED_TASK,
                [PARAM_UNCHANGED_ORDER_2]: PARAM_UNCHANGED_ORDER_2
            });
        });

        test('TXI-7385: bug - when no orders we must return task\'s metadata', () => {
            expect(
                getSelectedOrderOrTaskMetadata({
                    selectedOrder: null,
                    data: {
                        meta_info: {
                            [PARAM]: PARAM_TASK,
                            [PARAM_UNCHANGED_TASK]: PARAM_UNCHANGED_TASK
                        },
                        $view: {
                            unfilteredEvents: [
                                {
                                    type: EVENT_TYPE.MESSAGE,
                                    data: {metadata: {}}
                                },
                                {
                                    type: EVENT_TYPE.MESSAGE,
                                    data: {metadata: {}}
                                },
                                {
                                    type: EVENT_TYPE.MESSAGE,
                                    data: {metadata: {}}
                                }
                            ]
                        }
                    }
                })
            ).toEqual({
                [PARAM]: PARAM_TASK,
                [PARAM_UNCHANGED_TASK]: PARAM_UNCHANGED_TASK
            });
        });
    });
});
