import distance from '../distance';

test('utils:distance', () => {
    expect(distance([56, 36], [36, 56], 'kilometers')).toBe(2686.4156111711677);
});
