/**
 * @jest-environment jsdom
 */
import * as React from 'react';
import { shallow } from 'enzyme';
import { ReactElementsList } from 'typings/react';
import { jestSnapshotShallowTest } from 'testing/jest-utils';
import { Tooltip } from 'lego';
import { IconQuestion } from 'icons/IconQuestion';
import { HelpHint } from '..';

const snapshots: ReactElementsList = {
    'with passed className': <HelpHint className="className" />,
    'with isOpened prop': <HelpHint isOpen={true} />,
};

describe('HelpHint', () => {
    describe('renders', () => {
        jestSnapshotShallowTest(snapshots);
    });

    it('opens by click on icon', () => {
        const wrapper = shallow(<HelpHint />);

        wrapper.find(IconQuestion).simulate('click');
        expect(wrapper.find(Tooltip).prop('visible')).toBe(true);
    });

    it('opens and closes by click on icon', () => {
        const wrapper = shallow(<HelpHint />);

        wrapper.find(IconQuestion).simulate('click');
        expect(wrapper.find(Tooltip).prop('visible')).toBe(true);

        wrapper.find(IconQuestion).simulate('click');
        expect(wrapper.find(Tooltip).prop('visible')).toBe(false);
    });

    it('closes when it was rendered already opened', () => {
        const wrapper = shallow(<HelpHint isOpen={true} />);

        wrapper.find(IconQuestion).simulate('click');
        expect(wrapper.find(Tooltip).prop('visible')).toBe(false);
    });

    it('closes on document scroll', (done) => {
        const wrapper = shallow(
            <HelpHint isOpen={true} closeOnScroll={true} />,
        );

        window.dispatchEvent(new Event('scroll'));

        setTimeout(() => {
            expect(wrapper.find(Tooltip).prop('visible')).toBe(false);
            done();
        }, 100);
    });
});
