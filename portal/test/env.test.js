const ORIG_ENV = process.env;

beforeEach(function() {
    jest.resetModules();
    process.env = { ...ORIG_ENV };
});

test('empty env - no override', function() {
    process.env = {};

    expect(require('../utils/env').overrideEnv()).toBe(undefined);
});

test('YQL_TOKEN', function() {
    process.env = {
        YQL_TOKEN: 'abcde',
    };

    expect(require('../utils/env').overrideEnv()).toStrictEqual({
        YQL_TOKEN: 'abcde',
    });
});

test('ROBOT_MORDA_DEV_YQL_TOKEN', function() {
    process.env = {
        ROBOT_MORDA_DEV_YQL_TOKEN: 'abcde',
    };

    expect(require('../utils/env').overrideEnv()).toStrictEqual({
        ROBOT_MORDA_DEV_YQL_TOKEN: 'abcde',
        YQL_TOKEN: 'abcde',
    });
});

test('ROBOT_MORDA_DEV_YQL_TOKEN & YQL_TOKEN', function() {
    process.env = {
        YQL_TOKEN: '123456',
        ROBOT_MORDA_DEV_YQL_TOKEN: 'abcde',
    };

    expect(require('../utils/env').overrideEnv()).toStrictEqual({
        ROBOT_MORDA_DEV_YQL_TOKEN: 'abcde',
        YQL_TOKEN: '123456',
    });
});

test('ENV_MAPPING', function() {
    process.env = {
        ENV_MAPPING: 'YQL_TOKEN=SOMETHING',
        SOMETHING: '123456',
    };

    expect(require('../utils/env').overrideEnv()).toStrictEqual({
        ENV_MAPPING: 'YQL_TOKEN=SOMETHING',
        SOMETHING: '123456',
        YQL_TOKEN: '123456',
    });
});

test('ENV_MAPPING override', function() {
    process.env = {
        ENV_MAPPING: 'YQL_TOKEN=SOMETHING',
        SOMETHING: '123456',
        YQL_TOKEN: 'token',
    };

    expect(require('../utils/env').overrideEnv()).toStrictEqual({
        ENV_MAPPING: 'YQL_TOKEN=SOMETHING',
        SOMETHING: '123456',
        YQL_TOKEN: '123456',
    });
});

test('ENV_MAPPING override & ROBOT_MORDA_DEV_YQL_TOKEN', function() {
    process.env = {
        ENV_MAPPING: 'YQL_TOKEN=SOMETHING',
        SOMETHING: '123456',
        YQL_TOKEN: 'token',
        ROBOT_MORDA_DEV_YQL_TOKEN: 'robot_token',
    };

    expect(require('../utils/env').overrideEnv()).toStrictEqual({
        ENV_MAPPING: 'YQL_TOKEN=SOMETHING',
        SOMETHING: '123456',
        YQL_TOKEN: '123456',
        ROBOT_MORDA_DEV_YQL_TOKEN: 'robot_token',
    });
});
