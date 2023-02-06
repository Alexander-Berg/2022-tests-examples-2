import * as React from 'react';
import { mount, render } from 'enzyme';
import FeatureForm from './FeatureForm';

describe('FeatureForm', () => {
    // snapshots testing
    describe('renders', () => {
        it('with default props', () => {
            const spy = jest.fn();
            const component = render(
                <FeatureForm
                    {...{ onClose: spy, onSuccess: spy, onFail: spy }}
                />,
            );
            expect(component).toMatchSnapshot();
        });
    });

    // callbacks invoke testing
    describe('invokes callbacks', () => {
        it('#onClose', () => {
            const onClose = jest.fn();
            const component = mount(
                <FeatureForm
                    {...{ onClose, onSuccess: jest.fn(), onFail: jest.fn() }}
                />,
            );

            // write normal selector here
            const closer = component.find('.button_theme_normal');

            closer.simulate('click');

            expect(onClose).toHaveBeenCalledTimes(1);
            component.unmount();
        });
    });
});
