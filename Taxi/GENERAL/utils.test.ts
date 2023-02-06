import {generateMediaQueries, getPoint} from './utils';

test('generateMediaQueries - desc order', () => {
    expect(
        generateMediaQueries(size => size, {
            l: {maxContentWidth: 100, columns: 10},
            m: {maxContentWidth: 100, columns: 10},
            s: {maxContentWidth: 100, columns: 10},
            xs: {maxContentWidth: 100, columns: 10},
        }),
    ).toEqual('l\nm\ns\nxs');
});

test('getPrevPoint', () => {
    let utils = getPoint({
        l: {maxContentWidth: 100, columns: 10},
        m: {maxContentWidth: 100, columns: 10},
        s: {maxContentWidth: 100, columns: 10},
        xs: {maxContentWidth: 100, columns: 10},
    });

    expect(utils.getBigger('l')).toEqual(undefined);
    expect(utils.getBigger('m')).toEqual(['l', {maxContentWidth: 100, columns: 10}]);
    expect(utils.getSmaller('s')).toEqual(['xs', {maxContentWidth: 100, columns: 10}]);
    expect(utils.getSmaller('xs')).toEqual(undefined);

    utils = getPoint({
        l: undefined,
        m: {maxContentWidth: 100, columns: 10},
        xs: {maxContentWidth: 100, columns: 10},
    });

    expect(utils.getBigger('l')).toEqual(undefined);
    expect(utils.getBigger('m')).toEqual(undefined);
    expect(utils.getSmaller('l')).toEqual(['m', {maxContentWidth: 100, columns: 10}]);
    expect(utils.getSmaller('m')).toEqual(['xs', {maxContentWidth: 100, columns: 10}]);
    expect(utils.getSmallerOrEqual('m')).toEqual(['m', {maxContentWidth: 100, columns: 10}]);
    expect(utils.getSmallerOrEqual('l')).toEqual(['m', {maxContentWidth: 100, columns: 10}]);
});
