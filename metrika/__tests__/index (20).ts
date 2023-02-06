import { tree } from './fixtures/segmentsTreeDictionary';
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
    booleanFilters,
    booleanFiltersFalse,
    mixedFilters,
} from './fixtures/filters';
import { serialize } from '..';

describe('serialize', () => {
    it('works with incorrect data', () => {
        expect(serialize(nonExistentFilters, tree)).toMatchSnapshot();
    });
    describe('properly serialize value', () => {
        it('with string type', () => {
            expect(serialize(stringValueFilter, tree)).toMatchSnapshot();
        });
    });
    describe('list filters', () => {
        it('one value with inverted:false', () => {
            expect(serialize(listFilter, tree)).toMatchSnapshot();
        });
        it('one value with inverted:true', () => {
            expect(serialize(listFilterInverted, tree)).toMatchSnapshot();
        });
        it('several values with inverted:false', () => {
            expect(serialize(listFilters, tree)).toMatchSnapshot();
        });
        it('several values with inverted:true', () => {
            expect(serialize(listFiltersInverted, tree)).toMatchSnapshot();
        });
    });
    describe('tree filters', () => {
        it('one value with inverted:false', () => {
            expect(serialize(treeFilter, tree)).toMatchSnapshot();
        });
        it('one value with inverted:true', () => {
            expect(serialize(treeFilterInverted, tree)).toMatchSnapshot();
        });
        it('several values with inverted:false', () => {
            expect(serialize(treeFilters, tree)).toMatchSnapshot();
        });
        it('several values with inverted:true', () => {
            expect(serialize(treeFiltersInverted, tree)).toMatchSnapshot();
        });
    });
    describe('boolean filter', () => {
        it('with value:Yes', () => {
            expect(serialize(booleanFilters, tree)).toMatchSnapshot();
        });
        it('with value:No', () => {
            expect(serialize(booleanFiltersFalse, tree)).toMatchSnapshot();
        });
    });
    it('works with mixed filters', () => {
        expect(serialize(mixedFilters, tree)).toMatchSnapshot();
    });
});
