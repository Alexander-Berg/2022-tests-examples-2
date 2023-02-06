import {RC_TAG_PATTERN, VERSIONED_BRANCHES} from '../projects';

describe('RC_TAG_PATTERN', () => {
    test('rc-0.0.1', () => {
        expect(RC_TAG_PATTERN.test('rc-0.0.1')).toBe(true);
    });

    test('rc-0.0.1.1', () => {
        expect(RC_TAG_PATTERN.test('rc-0.0.1.1')).toBe(true);
    });

    test('rc-0.0.1-1234', () => {
        expect(RC_TAG_PATTERN.test('rc-0.0.1-1234')).toBe(false);
    });

    test('0.0.1', () => {
        expect(RC_TAG_PATTERN.test('0.0.1')).toBe(false);
    });

    test('r', () => {
        expect(RC_TAG_PATTERN.test('rc')).toBe(false);
    });

    test('parse version for rc-0.0.1', () => {
        const result = RC_TAG_PATTERN.exec('rc-0.0.1');
        expect(result.length).toBe(2);
        expect(result[1]).toBe('0.0.1');
    });
});

describe('VERSIONED_BRANCHES', () => {
    test('release-0.0.1', () => {
        expect(VERSIONED_BRANCHES.test('release-0.0.1')).toBe(true);
    });

    test('test-release-0.0.1', () => {
        expect(VERSIONED_BRANCHES.test('test-release-0.0.1')).toBe(false);
    });

    test('release-0.0.1-fix', () => {
        expect(VERSIONED_BRANCHES.test('release-0.0.1-fix')).toBe(false);
    });

    test('release-test', () => {
        expect(VERSIONED_BRANCHES.test('release-test')).toBe(false);
    });
});
