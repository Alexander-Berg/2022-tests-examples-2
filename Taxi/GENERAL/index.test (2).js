import {mapHierarchicalNamedEntityToOption} from './index';

describe('mapHierarchicalNamedEntityToOption', () => {
    it('превращает', () =>
        expect(
            mapHierarchicalNamedEntityToOption({
                name: 'name',
                _id: 'test',
                parent_id: 'parent',
            }),
        ).toEqual({
            value: 'test',
            parent_id: 'parent',
            label: 'name',
        }));
});
