import {exact} from '../asserts';

interface NotEmptyObj {
    x: 1;
}

test('IsObject<T>', () => {
    // negative cases
    exact<IsObject<number>, false>(true);
    exact<IsObject<number>, true>(false);

    exact<IsObject<boolean>, false>(true);
    exact<IsObject<boolean>, true>(false);

    exact<IsObject<any[]>, false>(true);
    exact<IsObject<any[]>, true>(false);

    exact<IsObject<Function>, false>(true);
    exact<IsObject<Function>, true>(false);

    exact<IsObject<never>, false>(true);
    exact<IsObject<never>, true>(false);

    exact<IsObject<unknown>, false>(true);
    exact<IsObject<unknown>, true>(false);

    exact<IsObject<any>, false>(true);
    exact<IsObject<any>, true>(false);

    exact<IsObject<null>, false>(true);
    exact<IsObject<null>, true>(false);

    exact<IsObject<undefined>, false>(true);
    exact<IsObject<undefined>, true>(false);

    exact<IsObject<object | number>, false>(true);
    exact<IsObject<object | number>, true>(false);

    exact<IsObject<{} | boolean>, false>(true);
    exact<IsObject<{} | boolean>, true>(false);

    exact<IsObject<Indexed | string>, false>(true);
    exact<IsObject<Indexed | string>, true>(false);

    exact<IsObject<object | any[]>, false>(true);
    exact<IsObject<object | any[]>, true>(false);

    exact<IsObject<object & number>, false>(true);
    exact<IsObject<object & number>, true>(false);

    exact<IsObject<{} & boolean>, false>(true);
    exact<IsObject<{} & boolean>, true>(false);

    exact<IsObject<Indexed & string>, false>(true);
    exact<IsObject<Indexed & string>, true>(false);

    exact<IsObject<Indexed & any[]>, false>(true);
    exact<IsObject<Indexed & any[]>, true>(false);

    // positive cases
    exact<IsObject<object>, true>(true);
    exact<IsObject<object>, false>(false);

    exact<IsObject<{}>, true>(true);
    exact<IsObject<{}>, false>(false);

    exact<IsObject<Indexed>, true>(true);
    exact<IsObject<Indexed>, false>(false);

    exact<IsObject<Indexed | Object | {}>, true>(true);
    exact<IsObject<Indexed | Object | {}>, false>(false);

    exact<IsObject<Indexed & Object & {}>, true>(true);
    exact<IsObject<Indexed & Object & {}>, false>(false);

    exact<IsObject<NotEmptyObj | {}>, true>(true);
    exact<IsObject<NotEmptyObj | {}>, false>(false);

    exact<IsObject<NotEmptyObj>, true>(true);
    exact<IsObject<NotEmptyObj>, false>(false);
});

test('IsObjectOrArray<T>', () => {
    // negative cases
    exact<IsObjectOrArray<number>, false>(true);
    exact<IsObjectOrArray<number>, true>(false);

    exact<IsObjectOrArray<boolean>, false>(true);
    exact<IsObjectOrArray<boolean>, true>(false);

    exact<IsObjectOrArray<any[]>, false>(false);
    exact<IsObjectOrArray<any[]>, true>(true);

    exact<IsObjectOrArray<Function>, false>(true);
    exact<IsObjectOrArray<Function>, true>(false);

    exact<IsObjectOrArray<never>, false>(true);
    exact<IsObjectOrArray<never>, true>(false);

    exact<IsObjectOrArray<unknown>, false>(true);
    exact<IsObjectOrArray<unknown>, true>(false);

    exact<IsObjectOrArray<any>, false>(true);
    exact<IsObjectOrArray<any>, true>(false);

    exact<IsObjectOrArray<null>, false>(true);
    exact<IsObjectOrArray<null>, true>(false);

    exact<IsObjectOrArray<undefined>, false>(true);
    exact<IsObjectOrArray<undefined>, true>(false);

    exact<IsObjectOrArray<object | number>, false>(true);
    exact<IsObjectOrArray<object | number>, true>(false);

    exact<IsObjectOrArray<{} | boolean>, false>(true);
    exact<IsObjectOrArray<{} | boolean>, true>(false);

    exact<IsObjectOrArray<Indexed | string>, false>(true);
    exact<IsObjectOrArray<Indexed | string>, true>(false);

    exact<IsObjectOrArray<object | any[]>, false>(false);
    exact<IsObjectOrArray<object | any[]>, true>(true);

    exact<IsObjectOrArray<object & number>, false>(true);
    exact<IsObjectOrArray<object & number>, true>(false);

    exact<IsObjectOrArray<{} & boolean>, false>(true);
    exact<IsObjectOrArray<{} & boolean>, true>(false);

    exact<IsObjectOrArray<Indexed & string>, false>(true);
    exact<IsObjectOrArray<Indexed & string>, true>(false);

    exact<IsObjectOrArray<Indexed & any[]>, false>(false);
    exact<IsObjectOrArray<Indexed & any[]>, true>(true);

    // positive cases
    exact<IsObjectOrArray<object>, true>(true);
    exact<IsObjectOrArray<object>, false>(false);

    exact<IsObjectOrArray<{}>, true>(true);
    exact<IsObjectOrArray<{}>, false>(false);

    exact<IsObjectOrArray<Indexed>, true>(true);
    exact<IsObjectOrArray<Indexed>, false>(false);

    exact<IsObjectOrArray<Indexed | Object | {}>, true>(true);
    exact<IsObjectOrArray<Indexed | Object | {}>, false>(false);

    exact<IsObjectOrArray<Indexed & Object & {}>, true>(true);
    exact<IsObjectOrArray<Indexed & Object & {}>, false>(false);

    exact<IsObjectOrArray<NotEmptyObj | {}>, true>(true);
    exact<IsObjectOrArray<NotEmptyObj | {}>, false>(false);

    exact<IsObjectOrArray<NotEmptyObj>, true>(true);
    exact<IsObjectOrArray<NotEmptyObj>, false>(false);
});

test('isArray<T>', () => {
    exact<IsArray<number[]>, true>(true);
    exact<IsArray<any[]>, true>(true);
    exact<IsArray<unknown[]>, true>(true);
    exact<IsArray<never[]>, true>(true);
    exact<IsArray<undefined[]>, true>(true);
    exact<IsArray<null[]>, true>(true);
    exact<IsArray<[]>, true>(true);

    exact<IsArray<null>, true>(false);
    exact<IsArray<undefined>, true>(false);
    exact<IsArray<never>, true>(false);
    exact<IsArray<unknown>, true>(false);
    exact<IsArray<{}>, true>(false);
    exact<IsArray<Indexed>, true>(false);
    exact<IsArray<number>, true>(false);
    exact<IsArray<any[] | number>, true>(false);
    exact<IsArray<any[] & number>, true>(false);
});
