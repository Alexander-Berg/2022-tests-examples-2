import {Graph, SampleList} from '../../types';
import {createSampleGraph, DAG_ERROR_MESSAGE} from '../graph';

describe('selectors/createSampleMap', function () {
    it('должен вернуть вершину с пустыми дочерними вершинами', function () {
        const input: SampleList = [
            {
                code: 'one',
                fields: [],
                sample_type: '',
            },
            {
                code: 'two',
                fields: [],
                sample_type: '',
            },
        ];
        const output: Graph = {
            one: [],
        };
        const graph = createSampleGraph(input[0].code)(input);

        expect(graph).toEqual(output);
    });

    it('должен вернуть две вершины, у первой должно быть одна дочерняя', function () {
        const input: SampleList = [
            {
                code: 'one',
                fields: [{
                    field_type: 'linked',
                    struct: 'two',
                    name: '',
                    field: '',
                }],
                sample_type: '',
            },
            {
                code: 'two',
                fields: [],
                sample_type: '',
            },
        ];
        const output: Graph = {
            one: ['two'],
            two: [],
        };
        const graph = createSampleGraph(input[0].code)(input);

        expect(graph).toEqual(output);
    });

    it('должен вернуть три вершины, у первой должно быть две дочерние', function () {
        const input: SampleList = [{
            code: 'one',
            fields: [{
                field_type: 'linked',
                struct: 'two',
                name: '',
                field: '',
            }, {
                field_type: 'linked',
                struct: 'three',
                name: '',
                field: '',
            }],
            sample_type: '',
        }, {
            code: 'two',
            fields: [],
            sample_type: '',
        }, {
            code: 'three',
            fields: [],
            sample_type: '',
        }];
        const output: Graph = {
            one: ['two', 'three'],
            two: [],
            three: [],
        };
        const graph = createSampleGraph(input[0].code)(input);

        expect(graph).toEqual(output);
    });

    it('должен вернуть три вершины, у первой должно быть две дочерние, у второй одна', function () {
        const input: SampleList = [{
            code: 'one',
            fields: [{
                name: '',
                field_type: 'linked',
                struct: 'two',
                field: '',
            }, {
                name: '',
                field_type: 'linked',
                struct: 'three',
                field: '',
            }],
            sample_type: '',
        }, {
            code: 'two',
            fields: [{
                name: '',
                field_type: 'linked',
                struct: 'three',
                field: '',
            }],
            sample_type: '',
        }, {
            code: 'three',
            fields: [],
            sample_type: '',
        }];
        const output: Graph = {
            one: ['two', 'three'],
            two: ['three'],
            three: [],
        };
        const graph = createSampleGraph(input[0].code)(input);

        expect(graph).toEqual(output);
    });

    it('должен бросать ошибку если граф зацикленный', function () {
        const input: SampleList = [{
            code: 'one',
            fields: [{
                field_type: 'linked',
                struct: 'two',
                name: '',
                field: '',
            }],
            sample_type: '',
        }, {
            code: 'two',
            fields: [{
                field_type: 'linked',
                struct: 'one',
                name: '',
                field: '',
            }],
            sample_type: '',
        }];

        expect(() => createSampleGraph(input[0].code)(input)).toThrowError(DAG_ERROR_MESSAGE);
    });

    it('должен вернуть множество вершин', function () {
        const input: SampleList = [{
            code: 'one',
            fields: [{
                field_type: 'linked',
                struct: 'two',
                name: '',
                field: '',
            }],
            sample_type: '',
        }, {
            code: 'two',
            fields: [{
                field_type: 'linked',
                struct: 'three',
                name: '',
                field: '',
            }, {
                field_type: 'linked',
                struct: 'four',
                name: '',
                field: '',
            }],
            sample_type: '',
        }, {
            code: 'three',
            fields: [],
            sample_type: '',
        }, {
            code: 'four',
            fields: [{
                field_type: 'linked',
                struct: 'five',
                name: '',
                field: '',
            }],
            sample_type: '',
        }, {
            code: 'five',
            fields: [],
            sample_type: '',
        }];
        const output: Graph = {
            one: ['two'],
            two: ['three', 'four'],
            three: [],
            four: ['five'],
            five: [],
        };
        const graph = createSampleGraph(input[0].code)(input);

        expect(graph).toEqual(output);
    });
});
