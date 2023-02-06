import {calculateCumulativeDistribution} from 'service/utils/math/cumulative-distribution';

describe('cumulative distribution', function () {
    it('just works', function () {
        const values = [2, 3, 1, 4, 5, 1, 3, 4, 2, 5];
        const distribution = calculateCumulativeDistribution(values);
        expect(distribution).toStrictEqual<ReturnType<typeof calculateCumulativeDistribution>>([
            {value: 1, f: 0.2},
            {value: 2, f: 0.4},
            {value: 3, f: 0.6},
            {value: 4, f: 0.8},
            {value: 5, f: 1.0}
        ]);
    });
});
