import * as React from 'react';

import { makeScreenshot } from '../../../../test-utils/screenshot';
import { Checkbox } from '../checkbox';
import { Checked, Size, Mode, Disabled } from '../checkbox.stories';
import { render, screen } from '@testing-library/react';
import { CheckboxSize } from '../../checkbox-radio-base/checkbox-radio-base-props';
import userEvent from '@testing-library/user-event';
import { CheckboxProps } from '../checkbox-props';

const title = 'checkbox';

const onCheck = jest.fn();

function renderCheckbox(props?: Partial<CheckboxProps>): void {
    render(<Checkbox size={CheckboxSize.S16} isChecked={false} onChange={onCheck} label={title} {...props} />);
}

function emulateClick(): void {
    userEvent.click(screen.getByText(title));
}

describe('Checkbox', () => {
    it('screenshot checked', async () => {
        await makeScreenshot(<Checked />, { width: 400, height: 400 });
    });

    it('screenshot size', async () => {
        await makeScreenshot(<Size />, { width: 400, height: 400 });
    });

    it('screenshot mode', async () => {
        await makeScreenshot(<Mode />, { width: 400, height: 400 });
    });

    it('screenshot disabled', async () => {
        await makeScreenshot(<Disabled />, { width: 400, height: 400 });
    });

    describe('logic', () => {
        beforeEach(() => {
            onCheck.mockClear();
        });

        /*
            todo: тут хочется проверять, что работает клик на label и сам чекбокс,
            лейбл можно найти по тексту, для checkbox для добавлять атрибут (role?)
            тут надо обсудить и договориться
        */
        it('should call onChange on label click', () => {
            renderCheckbox();
            emulateClick();

            expect(onCheck).toBeCalled();
        });

        it('should not call onClick when checkbox is disabled', () => {
            renderCheckbox({ isDisabled: true });
            emulateClick();

            expect(onCheck).not.toBeCalled();
        });
    });
});
