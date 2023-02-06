import * as React from 'react';

import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { makeScreenshot } from '../../../../test-utils/screenshot';

import { TextInput } from '../text-input';
import { TextInputProps, TextInputSize, TextInputType, TextInputView } from '../text-input-props';
import { screenshotsStories } from '../text-input.stories';

const onChange = jest.fn();
const onFocus = jest.fn();
const onBlur = jest.fn();
const onKeyUp = jest.fn();
const onKeyDown = jest.fn();
const onKeyPress = jest.fn();
const onMouseEnter = jest.fn();
const onMouseLeave = jest.fn();

function renderInput(props?: Partial<TextInputProps>): void {
    render(
        <TextInput
            type={TextInputType.Text}
            view={TextInputView.Default}
            size={TextInputSize.S36}
            onChange={onChange}
            onFocus={onFocus}
            onBlur={onBlur}
            onKeyUp={onKeyUp}
            onKeyDown={onKeyDown}
            onKeyPress={onKeyPress}
            onMouseEnter={onMouseEnter}
            onMouseLeave={onMouseLeave}
            {...props}
        />
    );
}

describe('TextInput', () => {
    let i = 0;
    describe.each(screenshotsStories)('screenshots', Story => {
        it(`screenshot ${i++}`, async () => {
            await makeScreenshot(<Story />, { width: 800, height: 160 });
        });
    });

    describe('logic', () => {
        beforeEach(() => {
            jest.clearAllMocks();
        });

        it('should be focused after render with autofocus prop', () => {
            renderInput({ withAutoFocus: true });

            const input = 'A';
            userEvent.keyboard(input);

            expect(onFocus).toBeCalled();
            expect(onChange).toBeCalledWith(input);
        });

        it('should be focused after Tab key pressed', () => {
            renderInput();

            const input = 'A';
            userEvent.tab();
            userEvent.keyboard(input);

            expect(onFocus).toBeCalled();
            expect(onChange).toBeCalledWith(input);
        });

        it('should not be focused and call onBlur after Tab key pressed, if input with autofocus', () => {
            renderInput({ withAutoFocus: true });

            userEvent.tab();
            userEvent.keyboard('A');

            expect(onBlur).toHaveBeenCalled();
            expect(onChange).not.toHaveBeenCalled();
        });

        it('should be focused after click on left icon', () => {
            const icon = <span data-testid="icon" />;
            renderInput({ iconLeft: icon });

            const input = 'A';
            userEvent.click(screen.getByTestId('icon'));
            userEvent.keyboard(input);

            expect(onFocus).toBeCalled();
            expect(onChange).toBeCalledWith(input);
        });

        it('should be focused after click on right icon', () => {
            const icon = <span data-testid="icon" />;
            renderInput({ iconRight: icon });

            const input = 'A';
            userEvent.click(screen.getByTestId('icon'));
            userEvent.keyboard(input);

            expect(onFocus).toBeCalled();
            expect(onChange).toBeCalledWith(input);
        });

        it('should focus and call onChange on clear click', () => {
            renderInput({ hasClear: true, value: 'foo' });

            // TODO: get rid of querySelector
            userEvent.click(document.querySelector('.text-input__icon_clear')!);

            expect(onFocus).toBeCalled();
            expect(onChange).toBeCalledWith('');
        });

        it('should not be focused if disabled', () => {
            renderInput({ isDisabled: true, withAutoFocus: true });

            expect(onFocus).not.toBeCalled();
        });

        it('should not be focused on Tab if disabled', () => {
            renderInput({ isDisabled: true });

            userEvent.tab();
            userEvent.keyboard('A');

            expect(onFocus).not.toBeCalled();
            expect(onChange).not.toBeCalled();
        });

        it('should call onKeyDown', () => {
            renderInput({ withAutoFocus: true });

            fireEvent.keyDown(document.activeElement!, { key: 'A' });

            expect(onKeyDown).toBeCalled();
        });

        it('should call onKeyUp', () => {
            renderInput({ withAutoFocus: true });

            fireEvent.keyUp(document.activeElement!, { key: 'A' });

            expect(onKeyUp).toBeCalled();
        });

        it('should call onKeyPress', () => {
            renderInput({ withAutoFocus: true });

            fireEvent.keyPress(
                document.activeElement!,
                // charCode required for keyPress event (https://github.com/testing-library/react-testing-library/issues/269#issuecomment-455854112)
                { key: 'A', charCode: 65 }
            );

            expect(onKeyPress).toBeCalled();
        });

        it('should call onMosuseEnter', () => {
            renderInput({ withAutoFocus: true });

            userEvent.hover(document.activeElement!);

            expect(onMouseEnter).toBeCalled();
        });

        it('should call onMouseLeave', () => {
            renderInput({ withAutoFocus: true });

            userEvent.hover(document.activeElement!);
            userEvent.unhover(document.activeElement!);

            expect(onMouseLeave).toBeCalled();
        });

        it('should provide correct ref', () => {
            const Input: React.FC = () => {
                const ref = React.useRef<HTMLInputElement | null>(null);
                const onClick = (): void => {
                    ref.current?.focus();
                };

                return (
                    <>
                        <button data-testid="button" onClick={onClick} />
                        <TextInput
                            ref={ref}
                            type={TextInputType.Text}
                            view={TextInputView.Default}
                            size={TextInputSize.S36}
                            onFocus={onFocus}
                        />
                    </>
                );
            };

            render(<Input />);
            userEvent.click(screen.getByTestId('button'));

            expect(onFocus).toBeCalled();
        });
    });
});
