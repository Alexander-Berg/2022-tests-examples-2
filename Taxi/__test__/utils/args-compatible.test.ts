import {exact} from '../asserts';

test('ArgsCompatible<T1, T2> - аргуметы T1 являются подмножеством T2', () => {
    exact<ArgsCompatible<[], []>, true>(true);
    exact<ArgsCompatible<[], [boolean]>, true>(true);
    exact<ArgsCompatible<[], [boolean?]>, true>(true);
    exact<ArgsCompatible<[boolean], [boolean]>, true>(true);
    exact<ArgsCompatible<[boolean?], [boolean]>, true>(true);
    exact<ArgsCompatible<[boolean], [boolean, number]>, true>(true);
    exact<ArgsCompatible<number[], []>, true>(true);
    exact<ArgsCompatible<[], string[]>, true>(true);
    exact<ArgsCompatible<any[], string[]>, true>(true);
    exact<ArgsCompatible<string[], [string]>, true>(true);

    exact<ArgsCompatible<[boolean, number], [boolean]>, true>(false);
    exact<ArgsCompatible<[boolean], []>, true>(false);
    exact<ArgsCompatible<[boolean?], []>, true>(false);
    exact<ArgsCompatible<[boolean], [boolean?]>, true>(false);
    exact<ArgsCompatible<[boolean], [number]>, true>(false);
    exact<ArgsCompatible<string[], any[]>, true>(false);
    exact<ArgsCompatible<string[], [any]>, true>(false);
});
