import * as React from 'react';

import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { Button } from '../button';
import { ButtonProps, ButtonSize, ButtonView } from '../button-props';

import { Size, TextButtonWithIcon, View, IconButton, Disabled, Rounded } from '../button.stories';
import { makeScreenshot } from '../../../../test-utils/screenshot';

const title = 'button';
const onButtonClick = jest.fn();
const onFocus = jest.fn();
const onBlur = jest.fn();

function renderButton(props?: Partial<ButtonProps>): void {
    render(
        <Button
            view={ButtonView.Shade}
            size={ButtonSize.S32}
            onClick={onButtonClick}
            onFocus={onFocus}
            onBlur={onBlur}
            {...props}
        >
            {title}
        </Button>
    );
}

function emulateClick(): void {
    userEvent.click(screen.getByText(title));
}

describe('Button', () => {
    describe('screenshot', () => {
        it('view', async () => {
            await makeScreenshot(<View />, { width: 400, height: 400 });
        });

        it('size', async () => {
            await makeScreenshot(<Size />, { width: 400, height: 400 });
        });

        it('text button with icons', async () => {
            await makeScreenshot(<TextButtonWithIcon />, { width: 400, height: 400 });
        });

        it('icon', async () => {
            await makeScreenshot(<IconButton />, { width: 400, height: 400 });
        });

        it('disabled', async () => {
            await makeScreenshot(<Disabled />, { width: 400, height: 400 });
        });

        it('rounded', async () => {
            await makeScreenshot(<Rounded />, { width: 400, height: 400 });
        });
    });

    describe('logic', () => {
        beforeEach(() => {
            onButtonClick.mockClear();
            onFocus.mockClear();
            onBlur.mockClear();
        });

        it('should call onClick', () => {
            renderButton();
            emulateClick();

            expect(onButtonClick).toBeCalled();
        });

        it('should not call onClick when button is disabled', () => {
            renderButton({ isDisabled: true });
            emulateClick();

            expect(onButtonClick).not.toBeCalled();
        });

        it('should call onFocus', () => {
            renderButton();
            fireEvent.focus(screen.getByText(title));

            expect(onFocus).toBeCalled();
        });

        it('should call onBlur', () => {
            renderButton();
            const btn = screen.getByText(title);
            fireEvent.focus(btn);
            fireEvent.blur(btn);

            expect(onBlur).toBeCalled();
        });
    });
});
