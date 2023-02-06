import {getTaskOrdersList, getTaskOrdersSelectOptions} from '../orders';
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

describe('services/tasks/selectors/orders', () => {
    describe('getTaskOrdersList', () => {
        test('all different orders', () => {
            expect(
                getTaskOrdersList({
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
            ).toEqual([
                {
                    id: ORDER_1,
                    label: `Заказ 1 · ${ORDER_1}`,
                    labelShort: 'Заказ 1',
                    metadata: {
                        order_id: ORDER_1,
                        [PARAM]: PARAM_ORDER_1,
                        [PARAM_UNCHANGED_TASK]: PARAM_UNCHANGED_TASK,
                        [PARAM_UNCHANGED_ORDER_1]: PARAM_UNCHANGED_ORDER_1
                    }
                },
                {
                    id: ORDER_2,
                    label: `Заказ 2 · ${ORDER_2}`,
                    labelShort: 'Заказ 2',
                    metadata: {
                        order_id: ORDER_2,
                        [PARAM]: PARAM_ORDER_2,
                        [PARAM_UNCHANGED_TASK]: PARAM_UNCHANGED_TASK,
                        [PARAM_UNCHANGED_ORDER_2]: PARAM_UNCHANGED_ORDER_2
                    }
                },
                {
                    id: ORDER_TASK,
                    label: `Заказ 3 · ${ORDER_TASK}`,
                    labelShort: 'Заказ 3',
                    metadata: {
                        order_id: ORDER_TASK,
                        [PARAM]: PARAM_TASK,
                        [PARAM_UNCHANGED_TASK]: PARAM_UNCHANGED_TASK
                    }
                }
            ]);
        });

        test('all message orders is the same', () => {
            expect(
                getTaskOrdersList({
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
                                            order_id: ORDER_1,
                                            [PARAM]: PARAM_ORDER_1,
                                            [PARAM_UNCHANGED_ORDER_1]: PARAM_UNCHANGED_ORDER_1
                                        }
                                    }
                                }
                            ]
                        }
                    }
                })
            ).toEqual([
                {
                    id: ORDER_1,
                    label: `Заказ 1 · ${ORDER_1}`,
                    labelShort: 'Заказ 1',
                    metadata: {
                        order_id: ORDER_1,
                        [PARAM]: PARAM_ORDER_1,
                        [PARAM_UNCHANGED_TASK]: PARAM_UNCHANGED_TASK,
                        [PARAM_UNCHANGED_ORDER_1]: PARAM_UNCHANGED_ORDER_1
                    }
                },
                {
                    id: ORDER_TASK,
                    label: `Заказ 2 · ${ORDER_TASK}`,
                    labelShort: 'Заказ 2',
                    metadata: {
                        order_id: ORDER_TASK,
                        [PARAM]: PARAM_TASK,
                        [PARAM_UNCHANGED_TASK]: PARAM_UNCHANGED_TASK
                    }
                }
            ]);
        });

        test('one of message is the same of task', () => {
            expect(
                getTaskOrdersList({
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
                                            order_id: ORDER_TASK,
                                            [PARAM]: PARAM_TASK,
                                            [PARAM_UNCHANGED_TASK]: PARAM_UNCHANGED_TASK
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
            ).toEqual([
                {
                    id: ORDER_2,
                    label: `Заказ 1 · ${ORDER_2}`,
                    labelShort: 'Заказ 1',
                    metadata: {
                        order_id: ORDER_2,
                        [PARAM]: PARAM_ORDER_2,
                        [PARAM_UNCHANGED_TASK]: PARAM_UNCHANGED_TASK,
                        [PARAM_UNCHANGED_ORDER_2]: PARAM_UNCHANGED_ORDER_2
                    }
                },
                {
                    id: ORDER_TASK,
                    label: `Заказ 2 · ${ORDER_TASK}`,
                    labelShort: 'Заказ 2',
                    metadata: {
                        order_id: ORDER_TASK,
                        [PARAM]: PARAM_TASK,
                        [PARAM_UNCHANGED_TASK]: PARAM_UNCHANGED_TASK
                    }
                }
            ]);
        });

        test('one task order', () => {
            expect(
                getTaskOrdersList({
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
            ).toEqual([
                {
                    id: ORDER_TASK,
                    label: ORDER_TASK,
                    labelShort: ORDER_TASK,
                    metadata: {
                        order_id: ORDER_TASK,
                        [PARAM]: PARAM_TASK,
                        [PARAM_UNCHANGED_TASK]: PARAM_UNCHANGED_TASK
                    }
                }
            ]);
        });

        test('no orders', () => {
            expect(
                getTaskOrdersList({
                    data: {
                        meta_info: {},
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
            ).toEqual([]);
        });
    });

    describe('services/tasks/selectors', () => {
        test('getTaskOrdersSelectOptions', () => {
            expect(
                getTaskOrdersSelectOptions({
                    data: {
                        meta_info: {order_id: ORDER_TASK},
                        $view: {
                            unfilteredEvents: [
                                {
                                    type: EVENT_TYPE.MESSAGE,
                                    data: {metadata: {order_id: ORDER_1}}
                                },
                                {
                                    type: EVENT_TYPE.MESSAGE,
                                    data: {metadata: {}}
                                },
                                {
                                    type: EVENT_TYPE.MESSAGE,
                                    data: {metadata: {order_id: ORDER_2}}
                                }
                            ]
                        }
                    }
                })
            ).toEqual([
                {
                    value: ORDER_1,
                    label: `Заказ 1 · ${ORDER_1}`
                },
                {
                    value: ORDER_2,
                    label: `Заказ 2 · ${ORDER_2}`
                },
                {
                    value: ORDER_TASK,
                    label: `Заказ 3 · ${ORDER_TASK}`
                }
            ]);
        });
    });
});
