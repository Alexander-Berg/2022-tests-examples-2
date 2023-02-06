import * as React from 'react';
import { shallow } from 'enzyme';

import Join from './Join';

describe('Join', () => {
    it('renders', () => {
        const comp = shallow(
            <Join separator="|">
                <span>1</span>
                <span>2</span>
            </Join>,
        );

        expect(comp).toMatchSnapshot();
    });

    it('renders empty', () => {
        const comp = shallow(<Join separator="|" />);

        expect(comp).toMatchSnapshot();
    });
});
