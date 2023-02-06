import {exact} from '../asserts';

test('GetOptionalKeys<T>', () => {
    exact<GetOptionalKeys<{a: number; b?: undefined; c?: {}}>, 'b' | 'c'>(true);
});

test('GetOptional<T>', () => {
    exact<GetOptional<{a: undefined; b?: string; c?: undefined}>, {b?: string; c?: undefined}>(true);
});

test('GetRequired<T>', () => {
    exact<GetRequired<{a: null; b?: string; c?: {}}>, {a: null}>(true);
});

test('DeepPartial<T>', () => {
    exact<
        DeepPartial<{
            s: {
                b: {
                    c: number;
                }[];
            };
        }>,
        {
            s?: {
                b?: {
                    c?: number;
                }[];
            };
        }
    >(true);
});

test('DeepRequired<T>', () => {
    exact<
        DeepRequired<{
            a?: {
                b?: {
                    c?: number | null;
                }[] | null;
            } | null;
        } | null>,
        {
            a: {
                b: {
                    c: number;
                }[];
            };
        }
    >(true);

    exact<DeepRequired<null>, never>(true);
    exact<DeepRequired<{a: null}>, {a: never}>(true);
});
