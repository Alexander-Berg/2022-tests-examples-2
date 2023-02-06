import {isReleaseCommit, isReleaseTag, parseReleaseBranch, parseReleaseCommit, parseReleaseTag} from '../utils';

test('isReleaseTag', () => {
    expect(isReleaseTag('tags/users/xxx/0.1234.1-release')).toBe(true);
    expect(isReleaseTag('tags/users/xxx/0.1234-release')).toBe(false);
});

test('isReleaseCommit', () => {
    expect(isReleaseCommit('v0.123.2-release')).toBe(true);
    expect(isReleaseCommit('v0.123-release')).toBe(false);
    expect(isReleaseCommit('vv0.123.2-release')).toBe(false);
    expect(isReleaseCommit('v0.123.2')).toBe(false);
});

test('parseReleaseBranch', () => {
    expect(parseReleaseBranch('releases/taxi-tariff-editor/123')).toBe(123);
});

test('parseReleaseTag', () => {
    expect(parseReleaseTag('tags/users/xxx/0.1234.1-release')).toEqual({build: 1234, patch: 1});
});

test('parseReleaseCommit', () => {
    expect(parseReleaseCommit('v0.123.2-release')).toEqual({build: 123, patch: 2});
});

test('getCurrentServiceVersion unstable', async () => {
    jest.resetModules();
    jest.mock('../../../common/vcs/arc', () => ({
        getCurrentBranch: (...args: any[]) => Promise.resolve({name: 'xxx'})
    }));

    const {getCurrentServiceVersion} = await import('../utils');

    expect((await getCurrentServiceVersion()).tag).toBe('unstable');
});

test('getCurrentServiceVersion release not  exists', async () => {
    jest.resetModules();
    jest.mock('../../../common/vcs/arc', () => ({
        getCurrentBranch: (...args: any[]) => Promise.resolve({name: 'releases/taxi-tariff-editor/124'}),
        arcCommand: () => Promise.resolve(),
        getCurrentUser: () => 'robot-taxi-frontend',
        getLog: () => Promise.resolve([{}])
    }));

    const {getCurrentServiceVersion} = await import('../utils');

    expect((await getCurrentServiceVersion()).id).toBe('0.124.0-release');
});

test('getCurrentServiceVersion release exists', async () => {
    jest.resetModules();
    jest.mock('../../../common/vcs/arc', () => ({
        getCurrentBranch: (...args: any[]) => Promise.resolve({name: 'releases/taxi-tariff-editor/124'}),
        arcCommand: () => Promise.resolve(),
        getLog: () =>
            Promise.resolve([
                {},
                {
                    message: 'v0.124.1'
                },
                {
                    message: 'v0.124.2-release'
                },
                {
                    message: 'v0.124.1-release'
                }
            ])
    }));

    const {getCurrentServiceVersion} = await import('../utils');

    expect((await getCurrentServiceVersion()).id).toBe('0.124.2-release');
});
