import * as React from 'react';

import { makeScreenshot } from '../../../../test-utils/screenshot';
import { Radio } from '../radio';
import { Checked, Disabled, Size } from '../radio.stories';
import { render, screen } from '@testing-library/react';
import { RadioSize } from '../../checkbox-radio-base/checkbox-radio-base-props';
import userEvent from '@testing-library/user-event';
import { RadioProps } from '../radio-props';

const title = 'radio';

const onCheck = jest.fn();

function renderRadio(props?: Partial<RadioProps>): void {
    render(<Radio size={RadioSize.S20} isChecked={false} onChange={onCheck} label={title} {...props} />);
}

function emulateClick(): void {
    userEvent.click(screen.getByText(title));
}

describe('Radio', () => {
    it('screenshot checked', async () => {
        await makeScreenshot(<Checked />, { width: 400, height: 400 });
    });

    it('screenshot size', async () => {
        await makeScreenshot(<Size />, { width: 400, height: 400 });
    });

    it('screenshot disabled', async () => {
        await makeScreenshot(<Disabled />, { width: 400, height: 400 });
    });

    describe('logic', () => {
        beforeEach(() => {
            onCheck.mockClear();
        });

        it('should call onChange on label click', () => {
            renderRadio();
            emulateClick();

            expect(onCheck).toBeCalled();
        });

        it('should not call onClick when radio is disabled', () => {
            renderRadio({ isDisabled: true });
            emulateClick();

            expect(onCheck).not.toBeCalled();
        });
    });
});
