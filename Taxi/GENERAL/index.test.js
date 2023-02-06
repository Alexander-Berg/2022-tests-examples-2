const {checkFeatureAvailable} = require('./index');

describe('checkFeatureAvailable', () => {
    test('enabled', () => {
        expect(checkFeatureAvailable({}, {})).toBe(false);
        expect(checkFeatureAvailable({}, {enabled: false})).toBe(false);
        expect(checkFeatureAvailable({}, {enabled: true})).toBe(true);
        expect(checkFeatureAvailable({country: 'rus'}, {enabled: false, countries: ['rus']})).toBe(
            false,
        );
    });

    test('include by country', () => {
        expect(checkFeatureAvailable({country: 'isr'}, {enabled: true, countries: ['rus']})).toBe(
            false,
        );

        expect(checkFeatureAvailable({country: 'rus'}, {enabled: true, countries: ['rus']})).toBe(
            true,
        );

        expect(
            checkFeatureAvailable(
                {country: 'isr', clientID: '1'},
                {enabled: true, countries: ['rus'], clients: ['1']},
            ),
        ).toBe(false);
    });

    test('include by clients', () => {
        expect(
            checkFeatureAvailable(
                {country: 'rus', clientID: '2'},
                {enabled: true, countries: ['rus'], clients: ['1']},
            ),
        ).toBe(false);

        expect(
            checkFeatureAvailable(
                {country: 'rus', clientID: '1'},
                {enabled: true, countries: ['rus'], clients: ['1', '2']},
            ),
        ).toBe(true);
    });

    test('exclude by clients', () => {
        expect(
            checkFeatureAvailable(
                {country: 'rus', clientID: '1'},
                {
                    enabled: true,
                    countries: ['rus'],
                    clients: ['1', '2'],
                    excludeBy: {clients: ['1']},
                },
            ),
        ).toBe(false);

        expect(
            checkFeatureAvailable(
                {country: 'rus', clientID: '2'},
                {
                    enabled: true,
                    countries: ['rus'],
                    clients: ['1', '2'],
                    excludeBy: {clients: ['1']},
                },
            ),
        ).toBe(true);
    });
});
