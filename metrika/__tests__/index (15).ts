import { Funnel } from '../typings';
import { serializeFunnel } from '../serialize';
import { INVALID_DATA } from 'app/lib/validData';

const trim = (str: string) => str.replace(/\s+/gm, '');

const CASES: Record<string, [Funnel, string]> = {
    'multiple steps': [
        {
            title: '',
            eventsBetweenSteps: true,
            singleSession: false,
            grouping: 'users',
            unit: 'seconds',
            steps: [
                {
                    title: '',
                    filters: [
                        {
                            tag: 'event',
                            combinePolicy: 'and',
                            items: [
                                {
                                    path: ['event1'],
                                    operator: '==',
                                    value: 'value1',
                                },
                            ],
                        },
                        {
                            tag: 'event',
                            combinePolicy: 'and',
                            items: [
                                {
                                    path: ['event2'],
                                    operator: '!=',
                                    value: 'value2',
                                },
                            ],
                        },
                    ],
                },
                {
                    title: '',
                    filters: [
                        {
                            tag: 'event',
                            combinePolicy: 'and',
                            items: [
                                {
                                    path: ['event3', 'level1', 'level2'],
                                },
                            ],
                        },
                    ],
                },
            ],
        },
        `
cond(
    ym:uft,
    (
        eventType=='EVENT_CLIENT' and eventLabel=='event1' and exists(paramsValueNormalized=='value1')
    or
        eventType=='EVENT_CLIENT' and eventLabel=='event2' and exists(paramsValueNormalized!='value2')
    )
    and 
        sessionType=='foreground'
)
cond(
    ym:uft,
        eventType=='EVENT_CLIENT' and eventLabel=='event3' and exists(paramsLevel1=='level1' and paramsLevel2=='level2')
    and 
        sessionType=='foreground'
)`,
    ],
    'all events operators': [
        {
            title: '',
            eventsBetweenSteps: true,
            singleSession: false,
            grouping: 'devices',
            unit: 'seconds',
            steps: [
                {
                    title: '',
                    filters: [
                        {
                            tag: 'event',
                            combinePolicy: 'and',
                            items: [{ path: ['e1'] }],
                        },
                        {
                            tag: 'event',
                            combinePolicy: 'and',
                            items: [
                                {
                                    operator: '==',
                                    path: ['e1'],
                                    value: 'v1',
                                },
                            ],
                        },
                        {
                            tag: 'event',
                            combinePolicy: 'and',
                            items: [
                                {
                                    operator: '!=',
                                    path: ['e1'],
                                    value: 'v1',
                                },
                            ],
                        },
                        {
                            tag: 'event',
                            combinePolicy: 'and',
                            items: [
                                {
                                    operator: '>',
                                    path: ['e1'],
                                    value: '10',
                                },
                            ],
                        },
                        {
                            tag: 'event',
                            combinePolicy: 'and',
                            items: [
                                {
                                    operator: '<',
                                    path: ['e1'],
                                    value: '10',
                                },
                            ],
                        },
                        {
                            tag: 'event',
                            combinePolicy: 'and',
                            items: [
                                {
                                    operator: '>=',
                                    path: ['e1'],
                                    value: '10',
                                },
                            ],
                        },
                        {
                            tag: 'event',
                            combinePolicy: 'and',
                            items: [
                                {
                                    operator: '<=',
                                    path: ['e1'],
                                    value: '10',
                                },
                            ],
                        },
                        {
                            tag: 'event',
                            combinePolicy: 'and',
                            items: [
                                {
                                    operator: '<>',
                                    path: ['e1'],
                                    value: ['10', '20'],
                                },
                            ],
                        },
                    ],
                },
            ],
        },
        `
cond(
    ym:uft,
    (
        eventType=='EVENT_CLIENT' and eventLabel=='e1'
    or
        eventType=='EVENT_CLIENT' and eventLabel=='e1' and exists(paramsValueNormalized=='v1')
    or
        eventType=='EVENT_CLIENT' and eventLabel=='e1' and exists(paramsValueNormalized!='v1')
    or
        eventType=='EVENT_CLIENT' and eventLabel=='e1' and exists(paramsValueDoubleOrNaN>10)
    or
        eventType=='EVENT_CLIENT' and eventLabel=='e1' and exists(paramsValueDoubleOrNaN<10)
    or
        eventType=='EVENT_CLIENT' and eventLabel=='e1' and exists(paramsValueDoubleOrNaN>=10)
    or
        eventType=='EVENT_CLIENT' and eventLabel=='e1' and exists(paramsValueDoubleOrNaN<=10)
    or
        eventType=='EVENT_CLIENT' and eventLabel=='e1' and exists(paramsValueDoubleOrNaN>=10 and paramsValueDoubleOrNaN<=20)
    )
)
        `,
    ],
    combinator: [
        {
            title: '',
            eventsBetweenSteps: true,
            singleSession: false,
            grouping: 'devices',
            unit: 'seconds',
            steps: [
                {
                    title: '',
                    filters: [
                        {
                            tag: 'event',
                            combinePolicy: 'and',
                            items: [{ path: ['1', '2'] }, { path: ['1', '3'] }],
                        },
                        {
                            tag: 'event',
                            combinePolicy: 'or',
                            items: [
                                { path: ['10', '20'] },
                                { path: ['10', '30'] },
                            ],
                        },
                    ],
                },
            ],
        },
        `
cond(
    ym:uft,
    (
            eventType=='EVENT_CLIENT'
        and
            eventLabel=='1' and exists(paramsLevel1=='2')
        and
            eventLabel=='1' and exists(paramsLevel1=='3')
    or
            eventType=='EVENT_CLIENT'
        and
        (
            eventLabel=='10' and exists(paramsLevel1=='20')
        or
            eventLabel=='10' and exists(paramsLevel1=='30')
        )
    )
)
        `,
    ],
};

describe('Funnel serialization', () => {
    for (const [name, [funnel, expected]] of Object.entries(CASES)) {
        // eslint-disable-next-line jest/valid-title
        test(name, () => {
            const serialized = serializeFunnel(funnel);
            if (serialized === INVALID_DATA) {
                throw new Error('Malformed funnel');
            }

            expect(trim(serialized)).toEqual(trim(expected));
        });
    }
});
