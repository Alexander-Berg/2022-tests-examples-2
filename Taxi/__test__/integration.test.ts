import {exact} from '_types/__test__/asserts';
import {OperationId, Service} from '_types/common/infrastructure';

import useOperation from '../use-operation';
import useSaga from '../use-saga';

test('Вывод результата в useOperation указан явно', () => {
    try {
        const operationId = 'operation_id';

        const {result} = useOperation<string>({operationId});
        exact<typeof result, string | undefined>(true);
    } catch {
        // ignore
    }
});

test('Вывод результата в useOperation из константы', () => {
    try {
        const operationId = 'operation_id' as OperationId<string>;

        const {result} = useOperation({operationId});
        exact<typeof result, string | undefined>(true);
    } catch {
        // ignore
    }
});

test('Вывод результата в useOperation из useSaga', () => {
    try {
        const {operationId} = useSaga({
            onLoad: function * (a: number, b?: {x: 2}) {
                return '2';
            }
        }, [1]);
        exact<typeof operationId, OperationId<string, [number, {x: 2}?]>>(true);

        const {result} = useOperation({operationId});
        exact<typeof result, string | undefined>(true);
    } catch {
        // ignore
    }
});

test('Вывод результата в useOperation из сервиса', () => {
    try {
         // tslint:disable-next-line: max-classes-per-file
        class TestService {
            public static toString = () => 'TestService';

            public static *method(a: number, b?: string) {
                return '1';
            }
        }

        const Srv = TestService as Service<typeof TestService>;

        const {result} = useOperation({operationId: Srv.method.id!});
        exact<typeof result, string | undefined>(true);
    } catch {
        // ignore
    }
});
