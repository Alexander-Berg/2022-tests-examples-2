import {exact} from '../asserts';

test('IsTuple<T>', () => {
    exact<IsTuple<[any]>, true>(true);
    exact<IsTuple<any[]>, false>(true);
});
