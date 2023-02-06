import {isNode, setEnv} from '../isNode';

test('isNode', () => {
    expect(isNode()).toBe(true);

    setEnv('web');
    expect(isNode()).toBe(false);
});
