import {exact} from '../../__test__/asserts';
import {ActionAPI, OperationId} from '../infrastructure';

test('OperationId', () => {
    // можно присвоить OperationId в string
    exact<OperationId<any> extends string ? 1 : 0, 1>(true);
    // но нельзя присвоить string в OperationId
    exact<string extends OperationId<any> ? 1 : 0, 1>(false);

    // завести айдишник можно через as
    const x = 'operation_id' as OperationId<string>;

    // айдишники с разными параметрами не совместимы
    exact<typeof x extends OperationId<number> ? 1 : 0, 0>(true);
    // айдишники с одинаковыми параметрами совместимы
    exact<typeof x extends OperationId<string> ? 1 : 0, 1>(true);
});

test('ActionAPI', () => {
    class TestClass {
        public method = (s: number) => s;
    }

    const actions: ActionAPI<TestClass> = undefined!;
    actions?.method?.(1);
});
