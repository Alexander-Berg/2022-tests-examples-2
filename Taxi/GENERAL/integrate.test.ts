import {integratePiecewiseFunction} from 'service/utils/math/integrate/integrate';

describe('integrate piecewise function', function () {
    it('just works', function () {
        const integral = integratePiecewiseFunction([
            {x: 0, y: 1},
            {x: 2, y: 3},
            {x: 1, y: 2},
            {x: 3, y: 2}
        ]);

        expect(integral).toBe(6.5);
    });
});
