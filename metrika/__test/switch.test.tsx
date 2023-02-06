import { makeScreenshot } from '@client-libs/test-utils/screenshot';
import {
    Checked,
    Disabled,
    MaxWidth,
    Multiline,
    Size,
    WithoutLabel,
} from '@client-libs/mindstorms/components/switch/switch.stories';
import React from 'react';
import { render, screen } from '@testing-library/react';
import { Switch } from '@client-libs/mindstorms/components/switch/switch';
import { SwitchProps, SwitchSize } from '@client-libs/mindstorms/components/switch/switch-props';
import userEvent from '@testing-library/user-event';

const onChange = jest.fn();
const title = 'Switch';
const isChecked = false;

function renderSwitch(props?: Partial<SwitchProps>): void {
    render(<Switch isChecked={isChecked} size={SwitchSize.S24} onChange={onChange} label={title} {...props} />);
}

function emulateClick(): void {
    userEvent.click(screen.getByText(title));
}

describe('Switch', () => {
    describe('screenshot', () => {
        it('checked', async () => {
            await makeScreenshot(<Checked />, { width: 400, height: 400 });
        });

        it('size', async () => {
            await makeScreenshot(<Size />, { width: 400, height: 400 });
        });

        it('without label', async () => {
            await makeScreenshot(<WithoutLabel />);
        });

        it('max width', async () => {
            await makeScreenshot(
                <div style={{ width: '400px' }}>
                    <MaxWidth />
                </div>,
                { width: 400, height: 400 }
            );
        });

        it('disabled', async () => {
            await makeScreenshot(<Disabled />, { width: 400, height: 400 });
        });

        it('multiline', async () => {
            await makeScreenshot(<Multiline />, { width: 400, height: 400 });
        });
    });

    describe('logic', () => {
        beforeEach(() => {
            onChange.mockClear();
        });

        it('should call onChange on label click', () => {
            renderSwitch();
            emulateClick();

            expect(onChange).toBeCalledWith(!isChecked);
        });

        it('should not call onChange when Switch is disabled', () => {
            renderSwitch({ isDisabled: true });
            emulateClick();

            expect(onChange).not.toBeCalled();
        });
    });
});
