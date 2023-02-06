import {utils} from '@constructor/compiler-common';
import ts from 'typescript';
import {
    createComponent,
    createEventHandler,
    createEventsSubscription,
    createJSXElement,
    createJSXSelfClosingElement,
    createJSXText,
    createStoreSubscription,
    createStoreSubscriptionWrapper,
    createUseEventsHook,
} from './ast';

const {printAst} = utils.ast;
const {formatContent} = utils.format;

describe('createJSXSelfClosingElement', () => {
    test('no attribute', () => {
        const result = printAst(createJSXSelfClosingElement({component: 'Test'}));
        expect(result).toBe(formatContent('<Test />'));
    });

    test('string attribute', () => {
        const result = printAst(createJSXSelfClosingElement({component: 'Test', props: {atr: 'atr'}}));
        expect(result).toBe(formatContent('<Test atr="atr"/>'));
    });

    test('number attribute', () => {
        const result = printAst(createJSXSelfClosingElement({component: 'Test', props: {atr: 1}}));
        expect(result).toBe(formatContent('<Test atr={1}/>'));
    });

    test('false attribute', () => {
        const result = printAst(createJSXSelfClosingElement({component: 'Test', props: {atr: false}}));
        expect(result).toBe(formatContent('<Test atr={false}/>'));
    });

    test('true attribute', () => {
        const result = printAst(createJSXSelfClosingElement({component: 'Test', props: {atr: true}}));
        expect(result).toBe(formatContent('<Test atr/>'));
    });

    test('null attribute', () => {
        const result = printAst(createJSXSelfClosingElement({component: 'Test', props: {atr: null}}));
        expect(result).toBe(formatContent('<Test atr={null}/>'));
    });

    test('undefined attribute', () => {
        const result = printAst(createJSXSelfClosingElement({component: 'Test', props: {atr: undefined}}));
        expect(result).toBe(formatContent('<Test atr={undefined}/>'));
    });

    test('object attribute', () => {
        const result = printAst(
            createJSXSelfClosingElement({
                component: 'Test',
                props: {
                    atr: {
                        a: 1,
                        b: {c: {d: ['2']}},
                    },
                },
            }),
        );

        expect(result).toBe(
            formatContent(`
            <Test 
                atr={{ 
                    a: 1, 
                    b: {c: {d: ['2'] }}, 
                }}
            />
        `),
        );
    });

    test('mixed attributes', () => {
        const result = printAst(
            createJSXSelfClosingElement({component: 'Test', props: {atr1: '1', atr2: 1, atr3: false, atr4: true}}),
        );

        expect(result).toBe(formatContent('<Test atr1="1" atr2={1} atr3={false} atr4/>'));
    });

    test('code attributes', () => {
        const result = printAst(
            createJSXSelfClosingElement({
                component: 'Test',
                props: {
                    ['#atr1']: '"1"',
                    ['#atr2']: 1,
                    ['#atr3']: false,
                    ['#atr4']: true,
                    ['#atr5']: '(...args) => console.log(...args)',
                },
            }),
        );

        expect(result).toBe(
            formatContent('<Test atr1="1" atr2={1} atr3={false} atr4 atr5={(...args) => console.log(...args)}/>'),
        );
    });
});

describe('createJSXElement', () => {
    test('with no children', () => {
        const result = printAst(createJSXElement({component: 'Test', props: {atr: 'atr'}}));
        expect(result).toBe(formatContent('<Test atr="atr"/>'));
    });

    test('with one child', () => {
        const inner = createJSXSelfClosingElement({component: 'Inner'});
        const result = printAst(createJSXElement({component: 'Test', props: {atr: 'atr'}, children: [inner]}));
        expect(result).toBe(formatContent('<Test atr="atr"><Inner /></Test>'));
    });

    test('with multiple children', () => {
        const inner1 = createJSXSelfClosingElement({component: 'Inner'});
        const inner2 = createJSXSelfClosingElement({component: 'Inner', props: {atr: true}});
        const result = printAst(createJSXElement({component: 'Test', props: {atr: 'atr'}, children: [inner1, inner2]}));
        expect(result).toBe(formatContent('<Test atr="atr"><Inner /><Inner atr/></Test>'));
    });
});

describe('createComponent', () => {
    test('string component', () => {
        const result = printAst(createComponent('Test', createJSXText('Text')));
        expect(result).toBe(
            formatContent(`
            function Test() {
                return (
                    <>Text</>
                )
            }
        `),
        );
    });

    test('plain component', () => {
        const inner1 = createJSXSelfClosingElement({component: 'Inner'});
        const inner2 = createJSXSelfClosingElement({component: 'Inner', props: {atr: true}});
        const outer = createJSXElement({component: 'Outer', props: {atr: 'atr'}, children: [inner1, inner2]});
        const result = printAst(createComponent('Test', outer));
        expect(result).toBe(
            formatContent(`
            function Test() {
                return (
                    <Outer atr="atr">
                        <Inner />
                        <Inner atr/>
                    </Outer>
                )
            }
        `),
        );
    });
});

describe('createSoreSubscription', () => {
    test('cerate subscription', () => {
        const result = printAst(createStoreSubscription('items', '({a}) => a.b.c'));
        expect(result).toBe(
            formatContent(
                `
                    const items = useStore(({a}) => a.b.c)
                `,
            ),
        );
    });

    test('multiple subscriptions', () => {
        const result = createStoreSubscriptionWrapper('Wrapper', 'Origin', [
            ['x', '({a}) => a.b.c'],
            ['y', '({d}) => d.e.f'],
        ]);

        expect(printAst(result)).toBe(
            formatContent(
                `
                    function Wrapper(props: Omit<OriginProps, 'x' | 'y'>) {
                        const x = useStore(({a}) => a.b.c);
                        const y = useStore(({d}) => d.e.f);
                        return <Origin {...props} x={x} y={y} />
                    }
                `,
            ),
        );
    });
});

describe('createEventsSubscription', () => {
    test('create event handler', () => {
        const result = printAst(createEventHandler('onLoad', '(e) => null'));
        expect(result).toBe(
            formatContent(
                `
                    const onLoad = useCallback(e => null, [])
                `,
            ),
        );
    });

    test('create useEvents hook', () => {
        const result = createUseEventsHook([
            ['url.queries.xxx', '() => 1'],
            ['url.queries.yyy', '() => 2'],
        ]);

        expect(printAst(result)).toBe(
            formatContent(
                `
                    useEvents([
                        ['url.queries.xxx', () => 1],
                        ['url.queries.yyy', () => 2]
                    ])
                `,
            ),
        );
    });

    test('multiple events', () => {
        const result = createStoreSubscriptionWrapper('Wrapper', 'Origin', [], {
            'on-item-selected': () => 1,
            'on-load': () => 2,
            'url.queries.xxx': () => 3,
        });

        expect(printAst(result)).toBe(
            formatContent(
                `
                    function Wrapper(props: Omit<OriginProps, 'onItemSelected' | 'onLoad'>) {
                        const onItemSelected = useCallback(() => 1, []);
                        const onLoad = useCallback(() => 2, []);
                        useEvents([
                            ['url.queries.xxx', () => 3]
                        ])
                        return <Origin {...props} onItemSelected={onItemSelected} onLoad={onLoad} />
                    }
                `,
            ),
        );
    });
});
