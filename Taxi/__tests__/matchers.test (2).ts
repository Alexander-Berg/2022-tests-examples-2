import {DEFAULT_RESOURCE_MODEL} from '../../../../consts';
import {preSave} from '../matchers';

describe('ResourcesService', () => {
    test('preSave не пропускает $view', () => {
        const actual = preSave({
            stable: DEFAULT_RESOURCE_MODEL
        });

        expect(actual.draft.data?.$view).toBeUndefined();
    });

    test('preSave без revision', () => {
        const actual = preSave({
            stable: {
                ...DEFAULT_RESOURCE_MODEL,
                id: 'id'
            }
        });

        expect(actual.query.id).toEqual('id');
        expect(actual.draft.data?.revision).toEqual(0);
    });

    test('preSave с revision 1', () => {
        const actual = preSave({
            stable: {
                ...DEFAULT_RESOURCE_MODEL,
                id: 'id',
                revision: 1
            }
        });

        expect(actual.query.id).toEqual('id');
        expect(actual.query.last_revision).toEqual(1);
        expect(actual.draft.data?.revision).toEqual(2);
    });
});
