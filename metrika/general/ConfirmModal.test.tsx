import { shallow } from 'enzyme';
import * as React from 'react';

import ConfirmModal from './ConfirmModal';

describe('ConfirmModal', () => {
    it('renders without body', () => {
        const yesCb = jest.fn();
        const noCb = jest.fn();

        const comp = shallow(
            <ConfirmModal
                title="Title"
                yesLabel="Yes"
                noLabel="No"
                visible={true}
                onYes={yesCb}
                onNo={noCb}
            />,
        );
        expect(comp).toMatchSnapshot();
    });

    it('renders with body', () => {
        const yesCb = jest.fn();
        const noCb = jest.fn();

        const comp = shallow(
            <ConfirmModal
                title="Title"
                body="Body"
                yesLabel="Yes"
                noLabel="No"
                visible={true}
                onYes={yesCb}
                onNo={noCb}
            />,
        );
        expect(comp).toMatchSnapshot();
    });
});
