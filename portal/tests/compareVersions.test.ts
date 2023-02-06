import { compareVersions } from '../compareVersions';

describe('home.compare-versions', function() {
    let signs = {
        '<': -1,
        '=': 0,
        '>': 1
    };
    function createAssertion(version1: unknown, sign: unknown, version2: unknown) {
        test('должно быть ' + [String(version1), sign, String(version2)].join(' '), function() {
            expect(compareVersions(version1 as string, version2 as string)).toEqual(signs[sign as keyof typeof signs]);
        });
    }

    describe('simple versions', function() {
        createAssertion('90', '>', 1.5);
        createAssertion(90, '>', '19');
        createAssertion('25', '>', '19.0');
        createAssertion('25.2', '>', '25');
        createAssertion('25.2', '>', '1.1');
        createAssertion(10, '>', 1);
        createAssertion(8, '>', 1);
        createAssertion(10, '>', 8);
        createAssertion('1.10', '>', '1.8');

        createAssertion('10', '=', 10);
        createAssertion('1.5', '=', 1.5);
        createAssertion(10, '=', '10');
        createAssertion(1.5, '=', '1.5');
        createAssertion('1.5', '=', '1.5');

        createAssertion(1, '<', 10);
        createAssertion(8, '<', 10);
        createAssertion(1, '<', 8);
        createAssertion(1.5, '<', '90');
        createAssertion('19', '<', 90);
        createAssertion('7', '<', '7.0');
        createAssertion('19.0', '<', '25');
        createAssertion('25', '<', '25.2');
        createAssertion('1.1', '<', '25.2');
    });

    describe('simple semversions', function() {
        createAssertion('1.0.0', '>', '0.0.9');
        createAssertion('1.0.0', '>', '0.4.0');
        createAssertion('0.4.0', '>', '0.0.8');
        createAssertion('0.0.1', '>', '0.0.0');
        createAssertion('1.10.0', '>', '1.1.0');
        createAssertion('1.10', '>', '1.8.0');

        createAssertion('1.0.9', '=', '1.0.9');

        createAssertion('0.0.9', '<', '1.0.0');
        createAssertion('0.4.0', '<', '1.0.0');
        createAssertion('0.0.8', '<', '0.4.0');
        createAssertion('0.0.0', '<', '0.0.1');
        createAssertion('1.1.0', '<', '1.10.0');
        createAssertion('1.8.0', '<', '1.10');
    });

    describe('semversions with letters at the end', function() {
        createAssertion('0.0.1a', '>', '0.0.1');
        createAssertion('25.9.1a', '>', '25.9.1');
        createAssertion('25.1a', '>', '25.1.9');
        createAssertion('25.1a', '>', '25.1.9');
        createAssertion('25.beta', '>', '25.1');
        createAssertion('25.1ubuntu-2', '>', '25.1ubuntu-1');
        createAssertion('1.10blabla', '>', '1.8blabla.0');
        createAssertion('1.1a.0', '>', '1.1.a.0');
        createAssertion('1.10.a.0', '>', '1.1a.0');

        createAssertion('25.1.9a', '=', '25.1.9a');

        createAssertion('0.0.1', '<', '0.0.1a');
        createAssertion('25.9.1', '<', '25.9.1a');
        createAssertion('25.1.9', '<', '25.1a');
        createAssertion('25.1.9', '<', '25.1a');
        createAssertion('25.1', '<', '25.beta');
        createAssertion('25.1ubuntu-0', '<', '25.1ubuntu-1');
        createAssertion('1.1.a.0', '<', '1.1a.0');
        createAssertion('1.1a.0', '<', '1.10.a.0');
        createAssertion('1.8blabla.0', '<', '1.10blabla');
    });

    describe('array, null and undefined versions', function() {
        test('nan', () => {
            expect(compareVersions(undefined, 0)).toBeNaN();
            expect(compareVersions(undefined, '1')).toBeNaN();
            // @ts-expect-error incorrect args
            expect(compareVersions(null, 0)).toBeNaN();
            // @ts-expect-error incorrect args
            expect(compareVersions(null, '1')).toBeNaN();
            // @ts-expect-error incorrect args
            expect(compareVersions(null, undefined)).toBeNaN();
            // @ts-expect-error incorrect args
            expect(compareVersions(undefined, null)).toBeNaN();
        });

        createAssertion([], '<', 0);
        createAssertion([4], '<', 5);
        createAssertion(3, '<', [4]);

        createAssertion(0, '>', []);
        createAssertion(5, '>', [4]);
        createAssertion([4], '>', 3);
    });
});
