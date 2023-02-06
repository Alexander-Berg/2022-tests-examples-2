import {ActivityConfigs} from '../../consts';
import {ConfigValue} from '../../types';
import {convertActivityFieldsToConfigValues, convertValueToForm} from '../converters';

const initialConfigValues = {
    [ActivityConfigs.DriverPointsActionCosts]: {
        value: {
            a: [-10, -10, -10],
            c: [1, 1, 2],
            o: [-5, -2, 0],
            n: [-5, -2, 0],
            p: [0, 0, 0],
            r: [-5, -2, 0],
            t: [0, 0, 0]
        },
        isDefault: false
    },
    [ActivityConfigs.DriverMetricsBlockingRulesActions]: {
        value: [
            {
                tanker_key_template: 'DriverMetricsTooManyOfferTimeoutsTempBlock',
                events_period_sec: 900,
                blocking_duration_sec: 900,
                rule_name: 'TooManyOfferTimeouts',
                tag: '20_100',
                max_blocked_cnt: 100,
                events_to_block_cnt: 2,
                events: [
                    {
                        name: 'offer_timeout'
                    },
                    {
                        name: 'auto_reorder',
                        tags: ['test1', ' test2']
                    },
                    {
                        name: 'auto_reorder',
                        tags: []
                    }
                ]
            }
        ],
        isDefault: false
    },
};

const valuesToForm = {
    [ActivityConfigs.DriverPointsActionCosts]: [
        ['a', -10, -10, -10],
        ['c', 1, 1, 2],
        ['o', -5, -2, 0],
        ['n', -5, -2, 0],
        ['p', 0, 0, 0],
        ['r', -5, -2, 0],
        ['t', 0, 0, 0]
    ],
    [ActivityConfigs.DriverMetricsBlockingRulesActions]: [
        {
            tanker_key_template: 'DriverMetricsTooManyOfferTimeoutsTempBlock',
            events_period_sec: 900,
            blocking_duration_sec: 900,
            rule_name: 'TooManyOfferTimeouts',
            tag: '20_100',
            max_blocked_cnt: 100,
            events_to_block_cnt: 2,
            events: [
                {
                    name: 'offer_timeout',
                    $view: {tagsDefine: 'overlook'}
                },
                {
                    name: 'auto_reorder',
                    $view: {tagsDefine: 'specify'},
                    tagsStr: 'test1, test2'
                },
                {
                    name: 'auto_reorder',
                    $view: {tagsDefine: 'without'},
                    tagsStr: ''
                }
            ]
        }
    ],
};

const valuesFromForm = {
    [ActivityConfigs.DriverPointsActionCosts]: {
        value: [
            ['a', '-10', -10, -10],
            ['c', 1, 1, 2],
            ['o', -5, -2, 0],
            ['n', -5, '-2', 0],
            ['p', 0, 0, 0],
            ['r', '-5', -2, 0],
            ['t', 0, 0, 0]
        ],
        isDefault: false
    },
    [ActivityConfigs.DriverMetricsBlockingRulesActions]: {
        value: [
            {
                tanker_key_template: 'DriverMetricsTooManyOfferTimeoutsTempBlock',
                events_period_sec: '900',
                blocking_duration_sec: 900,
                rule_name: 'TooManyOfferTimeouts',
                tag: '20_100',
                max_blocked_cnt: 100,
                events_to_block_cnt: '2',
                events: [
                    {
                        name: 'offer_timeout',
                        $view: {tagsDefine: 'overlook'}
                    },
                    {
                        name: 'auto_reorder',
                        $view: {tagsDefine: 'specify'},
                        tagsStr: 'test1, test2'
                    },
                    {
                        name: 'auto_reorder',
                        $view: {tagsDefine: 'without'},
                        tagsStr: ''
                    }
                ]
            }
        ],
        isDefault: false
    },
};

describe('bundles/activity/sagas/converters', () => {
    test('Правильно конвертирует конфиг DRIVER_POINTS_ACTION_COSTS для формы', () => {
        expect(
            convertValueToForm(ActivityConfigs.DriverPointsActionCosts, (initialConfigValues[
                ActivityConfigs.DriverPointsActionCosts
            ].value as any) as ConfigValue)
        ).toMatchObject(valuesToForm[ActivityConfigs.DriverPointsActionCosts]);
    });

    test('Правильно конвертирует конфиг DRIVER_METRICS_BLOCKING_RULES_ACTIONS для формы', () => {
        expect(
            convertValueToForm(ActivityConfigs.DriverMetricsBlockingRulesActions, (initialConfigValues[
                ActivityConfigs.DriverMetricsBlockingRulesActions
            ].value as any) as ConfigValue)
        ).toMatchObject(valuesToForm[ActivityConfigs.DriverMetricsBlockingRulesActions]);
    });

    test('Правильно конвертирует конфиги из формы в первоначальный вид c конвертацией типов', () => {
        expect(convertActivityFieldsToConfigValues(valuesFromForm)).toMatchObject(initialConfigValues);
    });
});
