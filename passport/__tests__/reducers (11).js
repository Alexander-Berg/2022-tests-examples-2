import reducers from '../reducers';

jest.mock('../user_question/reducers', (state = {}) => state);
jest.mock('../last_auth/reducers', (state = {}) => state);

describe('Morda.Security.reducers', () => {
    it('should have 1 key', () => {
        expect(Object.keys(reducers()).length).toBe(1);
    });
    it('should return default state', () => {
        expect(reducers().securityLevel).toEqual({});
    });
});
