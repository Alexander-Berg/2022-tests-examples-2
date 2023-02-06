import {ActionType} from '../../common/enums';
import {DEFAULT_BULK_EVENT, EVENT_NAME_CELL_NAME, EVENT_TOPIC_CELL_NAME, GLOBAL_TAGS_CELL_NAME} from '../consts';
import {convertRulesToCSV} from '../utils';

describe('convertRulesToCSV', () => {
    it('Парсинг правил в CSV со всеми заполненными значениями', () => {
        const csv = convertRulesToCSV('Loyalty', {
            moscow: [
                {
                    additional_params: {
                        tags: '\'tags::loyalty_90\' OR \'tags::loyalty_80\'',
                    },
                    actions: [
                        {
                            tags: '\'event::tariff_econom\' OR \'event::tariff_start\'',
                            action: [
                                {type: ActionType.Loyalty, value: 10},
                            ]
                        }
                    ],
                    events: [DEFAULT_BULK_EVENT],
                    name: 'Loyalty',
                }
            ],
            piter: [
                {
                    additional_params: {
                        tags: '\'tags::loyalty_90\'',
                    },
                    actions: [
                        {
                            tags: '\'event::tariff_econom\'',
                            action: [
                                {type: ActionType.Loyalty, value: 20},
                            ]
                        },
                        {
                            tags: '\'event::tariff_start\'',
                            action: [
                                {type: ActionType.Loyalty, value: 50},
                            ]
                        }
                    ],
                    events: [{
                        topic: 'order',
                        name: 'auto_reorder',
                    }],
                    name: 'Loyalty',
                }
            ],
            novgorod: [
                {
                    additional_params: {
                        tags: '\'tags::loyalty_90\'',
                    },
                    actions: [
                        {
                            tags: '\'event::tariff_econom\'',
                            action: [
                                {type: ActionType.Loyalty, value: 20},
                            ]
                        }
                    ],
                    events: [DEFAULT_BULK_EVENT],
                    name: 'Loyalty-2',
                }
            ],
        });

        const result = `Loyalty,econom,start,${GLOBAL_TAGS_CELL_NAME},${EVENT_TOPIC_CELL_NAME},${EVENT_NAME_CELL_NAME}\nmoscow,10,10,loyalty_90 loyalty_80,order,complete\npiter,20,50,loyalty_90,order,auto_reorder`;
        expect(csv).toBe(result);
    });

    it('Парсинг правил в CSV с частично не заполненными или не валидными значениями', () => {
        const csv = convertRulesToCSV('Loyalty', {
            moscow: [
                {
                    additional_params: {
                        tags: '\'tags::loyalty_90\' OR \'tags::loyalty_80\'',
                    },
                    actions: [
                        {
                            tags: '\'event::tariff_econom\' OR \'event::tariff_start\'',
                            action: [
                                {type: ActionType.Loyalty, value: 10},
                            ]
                        }
                    ],
                    name: 'Loyalty',
                }
            ],
            piter: [
                {
                    additional_params: {
                        tags: '\'sdfsdfees\'',
                    },
                    actions: [
                        {
                            tags: '\'sdfwe423f\'',
                            action: [
                                {type: ActionType.Loyalty, value: 20},
                            ]
                        },
                        {
                            tags: '\'dasd22\'',
                            action: [
                                {type: ActionType.Loyalty, value: 50},
                            ]
                        },
                        {
                            tags: '\'event::tariff_econom\'',
                            action: [
                                {type: ActionType.Dispatch, time: [2]},
                            ]
                        }
                    ],
                    name: 'Loyalty',
                }
            ],
            novgorod: [
                {
                    additional_params: {
                        tags: '\'tags::loyalty_90\'',
                    },
                    actions: [
                        {
                            tags: '\'event::tariff_econom\'',
                            action: [
                                {type: ActionType.Loyalty, value: 20},
                            ]
                        }
                    ],
                    name: 'Loyalty-2',
                }
            ],
        });

        const result = `Loyalty,econom,start,${GLOBAL_TAGS_CELL_NAME},${EVENT_TOPIC_CELL_NAME},${EVENT_NAME_CELL_NAME}\nmoscow,10,10,loyalty_90 loyalty_80,,\npiter,,,,,`;
        expect(csv).toBe(result);
    });
});
