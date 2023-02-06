import * as React from 'react';

import { makeScreenshot } from '@client-libs/test-utils/screenshot';
import {
    Disabled,
    Primary,
    WithDisabledOptions,
    WithEllipsis,
    View,
    Content,
} from '@client-libs/mindstorms/components/radio-button/radio-button.stories';
import {
    RadioButtonProps,
    RadioButtonSize,
    RadioButtonView,
} from '@client-libs/mindstorms/components/radio-button/radio-button-props';
import { fireEvent, render, screen } from '@testing-library/react';
import { RadioButton } from '@client-libs/mindstorms/components/radio-button/radio-button';
import userEvent from '@testing-library/user-event';

const height = 200;

const onChange = jest.fn();
const onFocus = jest.fn();
const onBlur = jest.fn();

const defaultProps = {
    value: 'button0',
    options: [
        { value: 'button0', text: 'Button 36' },
        { value: 'button1', text: 'Button 36' },
        { value: 'button2', text: 'Button 36' },
        { value: 'button3', text: 'Button 36' },
    ],
    onChange: (): null => null,
    view: RadioButtonView.Shade,
    size: RadioButtonSize.S44,
};

function renderRadioButton(props?: Partial<RadioButtonProps>): void {
    render(<RadioButton {...defaultProps} onChange={onChange} {...props} />);
}

function emulateClick(value = 'button2'): void {
    userEvent.click(screen.getByDisplayValue(value));
}

describe('RadioButton', () => {
    it('screenshot radio-button with content', async () => {
        await makeScreenshot(<Content />, { width: 1000, height: 400 });
    });

    it('screenshot view radio-button', async () => {
        await makeScreenshot(<View />, { width: 450, height });
    });

    it('screenshot radio-button with disabled options', async () => {
        await makeScreenshot(<WithDisabledOptions />, { width: 450, height });
    });

    it('screenshot disabled radio-button', async () => {
        await makeScreenshot(<Disabled />, { width: 450, height });
    });

    it('screenshot primary radio-button', async () => {
        await makeScreenshot(<Primary />, { width: 550, height });
    });

    it('screenshot radio-button with ellipsis', async () => {
        await makeScreenshot(<WithEllipsis />, { width: 450, height });
    });

    describe('logic', () => {
        beforeEach(() => {
            onChange.mockClear();
            onBlur.mockClear();
            onFocus.mockClear();
        });

        it('should call onChange on label click', () => {
            renderRadioButton();
            emulateClick();

            expect(onChange).toBeCalled();
        });

        it('should not call onChange on label click when radio-button is disabled', () => {
            renderRadioButton({ isDisabled: true });
            emulateClick();

            expect(onChange).not.toBeCalled();
        });

        it('should not call onChange on label click when option of radio-button is disabled', () => {
            renderRadioButton({
                ...defaultProps,
                options: [
                    { value: 'button0', text: 'Button 36' },
                    { value: 'button1', text: 'Button 36', isDisabled: true },
                    { value: 'button2', text: 'Button 36' },
                    { value: 'button3', text: 'Button 36' },
                ],
            });
            emulateClick('button1');

            expect(onChange).not.toBeCalled();
        });

        it('should call onFocus', () => {
            const testId = 'radio-super';

            renderRadioButton({ testId, onFocus });
            const radioButton = screen.getByTestId(testId);
            fireEvent.focus(radioButton);

            expect(onFocus).toBeCalled();
        });

        it('should call onBlur', () => {
            const testId = 'radio-super';

            renderRadioButton({ testId, onFocus, onBlur });
            const radioButton = screen.getByTestId(testId);
            fireEvent.focus(radioButton);
            fireEvent.blur(radioButton);

            expect(onBlur).toBeCalled();
        });
    });
});
