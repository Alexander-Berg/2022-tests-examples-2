import * as React from 'react';
import { DateTitle } from '..';
import { shallow } from 'enzyme';

beforeAll(() => {
    const BN = jest.fn();

    BN.mockImplementation(() => ({
        isNonWorkDay() {
            return false;
        },
    }));

    // @ts-ignore
    global.BN = BN;
});

describe('DateTitle', () => {
    test('should format date with default format if none provided', () => {
        const title = shallow(<DateTitle value="2019-12-02" />);
        expect(title.contains('02.12.2019')).toBe(true);
    });

    test('should format date with provided format if any passed to', () => {
        const title = shallow(<DateTitle value="2019-12-02" format="YYYY" />);
        expect(title.contains('2019')).toBe(true);
    });
});

afterAll(() => {
    // @ts-ignore
    delete global.BN;
});
