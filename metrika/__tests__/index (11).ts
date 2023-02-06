import { createApiSerializer, IdToName } from '../api';

import {
    nonExistentFilters,
    listFilter,
    listFilters,
    listFilterInverted,
    listFiltersInverted,
    treeFilter,
    treeFilterInverted,
    treeFilters,
    treeFiltersInverted,
    stringValueFilter,
    mixedFilters,
} from './fixtures/filters';
import { tree } from './fixtures/segmentsTreeDictionary';

const idToName: IdToName = (id, payload) => {
    const { type, value } = payload ?? {};
    const item = tree[id];

    if (!item) {
        return '';
    }

    if (type === 'tree') {
        return item.dims[value];
    }

    return item.dim;
};

const serializeToApiFormat = createApiSerializer();

describe('serialize', () => {
    it('works with incorrect data', () => {
        expect(
            serializeToApiFormat(nonExistentFilters, idToName),
        ).toMatchSnapshot();
    });
    describe('properly serialize value', () => {
        it('with string type', () => {
            expect(
                serializeToApiFormat(stringValueFilter, idToName),
            ).toMatchSnapshot();
        });
    });
    describe('list filters', () => {
        it('one value with inverted:false', () => {
            expect(
                serializeToApiFormat(listFilter, idToName),
            ).toMatchSnapshot();
        });
        it('one value with inverted:true', () => {
            expect(
                serializeToApiFormat(listFilterInverted, idToName),
            ).toMatchSnapshot();
        });
        it('several values with inverted:false', () => {
            expect(
                serializeToApiFormat(listFilters, idToName),
            ).toMatchSnapshot();
        });
        it('several values with inverted:true', () => {
            expect(
                serializeToApiFormat(listFiltersInverted, idToName),
            ).toMatchSnapshot();
        });
    });
    describe('tree filters', () => {
        it('one value with inverted:false', () => {
            expect(
                serializeToApiFormat(treeFilter, idToName),
            ).toMatchSnapshot();
        });
        it('one value with inverted:true', () => {
            expect(
                serializeToApiFormat(treeFilterInverted, idToName),
            ).toMatchSnapshot();
        });
        it('several values with inverted:false', () => {
            expect(
                serializeToApiFormat(treeFilters, idToName),
            ).toMatchSnapshot();
        });
        it('several values with inverted:true', () => {
            expect(
                serializeToApiFormat(treeFiltersInverted, idToName),
            ).toMatchSnapshot();
        });
    });
    it('works with mixed filters', () => {
        expect(serializeToApiFormat(mixedFilters, idToName)).toMatchSnapshot();
    });
});
