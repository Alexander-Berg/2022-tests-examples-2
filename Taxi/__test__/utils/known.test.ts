import {exact} from '../asserts';

test('KnownKeys<T>', () => {
    exact<
        KnownKeys<{
            [str: string]: any;
            [num: number]: unknown;
            x: number;
            y?: string;
        }>,
        'x' | 'y'
    >(true);

    exact<
        KnownKeys<{
            x: number;
            y?: string;
        }>,
        'x' | 'y'
    >(true);

    exact<KnownKeys<{
        [x: string]: string;
        x: string;
    } & {
        [x: string]: string;
        y: string;
    }>, 'x' | 'y'>(true);

    exact<KnownKeys<{
        [x: string]: string;
        x: string;
    } | {
        [x: string]: string;
        y: string;
    }>, never>(true);

    exact<KnownKeys<undefined>, never>(true);
    exact<KnownKeys<null>, never>(true);
    exact<KnownKeys<never>, never>(true);
    exact<KnownKeys<{}>, never>(true);
    exact<KnownKeys<number>, never>(true);
    exact<KnownKeys<any>, never>(true);
});

test('PickKnown<T>', () => {
    exact<
        PickKnown<{
            [str: string]: any;
            [num: number]: unknown;
            x: number;
            y?: string;
        }>,
        {
            x: number;
            y?: string;
        }
    >(true);

    exact<PickKnown<{
        [x: string]: string;
        x: string;
    } & {
        [x: string]: string;
        y: string;
    }>, {
        x: string;
        y: string;
    }>(true);

    exact<PickKnown<{
        [x: string]: string;
        x: string;
    } | {
        [x: string]: string;
        y: string;
    }>, {
        x: string
    } | {
        y: string
    }>(true);

    exact<PickKnown<undefined>, {}>(true);
    exact<PickKnown<null>, {}>(true);
    exact<PickKnown<never>, {}>(true);
    exact<PickKnown<{}>, {}>(true);
    exact<PickKnown<number>, {}>(true);
    exact<PickKnown<any>, {}>(true);
});
