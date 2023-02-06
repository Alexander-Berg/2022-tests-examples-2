import {IGenerationScheme} from './components-scheme';

function Ctr(scheme: IGenerationScheme) {}

test('"on" expects functions', () => {
    const a = new Ctr({
        api: {},
        queries: {},
        root: {
            $page: {
                // @ts-expect-error
                onLoad: 2,
            },
        },
    });

    const b = new Ctr({
        api: {},
        queries: {},
        root: {
            $page: {
                onLoad: () => null,
            },
        },
    });
});

test('query events', () => {
    const a = new Ctr({
        api: {},
        queries: {},
        root: {
            $page: {
                'url.query.xxx': () => null,
                'url.query': () => null,
            },
        },
    });

    const b = new Ctr({
        api: {},
        queries: {},
        root: {
            $page: {
                // @ts-expect-error
                'url.query.xxx': 2,
                // @ts-expect-error
                'url.query': 2,
            },
        },
    });

    const c = new Ctr({
        api: {},
        queries: {},
        root: {
            $page: {
                // @ts-expect-error
                'url.xxx': () => null,
            },
        },
    });
});

test('"#" expects functions', () => {
    const a = new Ctr({
        api: {},
        queries: {},
        root: {
            $page: {
                $code: {
                    // @ts-expect-error
                    '#code': 2,
                },
            },
        },
    });

    const b = new Ctr({
        api: {},
        queries: {},
        root: {
            $page: {
                $code: {
                    '#code': ({$queries}) => $queries.xxx.result,
                },
            },
        },
    });

    const c = new Ctr({
        api: {},
        queries: {},
        root: {
            $page: {
                $code: {
                    // @ts-expect-error
                    '#code': ({$queries}) => $queries.xxx.unknown,
                },
            },
        },
    });
});

test('default component keys', () => {
    const a = new Ctr({
        api: {},
        queries: {},
        root: {
            $page: {
                $box: {},
                $code: {},
                $input: {},
                $list: {},
                $page: {},
                $select: {},
                $table: {},
                $tabs: {},
            },
        },
    });
});

test('custom component keys require _type', () => {
    const a = new Ctr({
        api: {},
        queries: {},
        root: {
            $page: {
                // @ts-expect-error
                $customTabs: {},
            },
        },
    });

    const b = new Ctr({
        api: {},
        queries: {},
        root: {
            $page: {
                $$customTabs: {
                    _type: 'tabs',
                },
            },
        },
    });
});

test('text component keys', () => {
    const x = new Ctr({
        api: {},
        queries: {},
        root: {
            $page: {
                $$someText: 'xxxx',
            },
        },
    });
});

test('common components in camelCase', () => {
    const x = new Ctr({
        api: {},
        queries: {},
        root: {
            $page: {
                $sidePanelFooter: {
                    $box: {},
                },
            },
        },
    });
});
