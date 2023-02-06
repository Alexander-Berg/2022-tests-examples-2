import actions from '../actions';

describe('actions', () => {
    it('returns proper set of actions', () => {
        expect(typeof actions === 'object').toBe(true);
        expect(typeof actions.switch === 'function').toBe(true);
        expect(Object.keys(actions)).toEqual(['switch']);
    });
});
