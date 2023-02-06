import { expect } from 'chai';
import { getNavigatorFields, navigatorFields } from '../navigator';

describe('navigatorFactor', () => {
    const appName = 'appName';

    it('with fields', () => {
        const result = getNavigatorFields(
            {
                navigator: {
                    appName,
                },
            } as any,
            [appName],
        );
        expect(result).to.be.deep.eq([appName]);
    });

    it('without fields', () => {
        const result = getNavigatorFields({} as any);
        expect(result).to.be.deep.eq(navigatorFields.map(() => undefined));
    });

    it('with default fields', () => {
        const result = getNavigatorFields({
            navigator: navigatorFields.reduce((fields, field) => {
                fields[field] = field;
                return fields;
            }, {} as Record<string, string>),
        } as any);
        expect(result).to.be.deep.eq(navigatorFields);
    });
});
