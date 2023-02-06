import * as React from 'react';
import { ButtonSize, ButtonView } from '@client-libs/mindstorms/components/button/button-props';
import userEvent from '@testing-library/user-event';
import { screen, render, fireEvent, act } from '@testing-library/react';
import { ForwardedRef, forwardRef } from 'react';
import { Dropdown, DropdownApi } from '@client-libs/mindstorms/components/dropdown/dropdown';
import {Disabled, TestExample} from '@client-libs/mindstorms/components/dropdown/dropdown.stories';
import { makeScreenshot } from '@client-libs/test-utils/screenshot';

jest.useFakeTimers();

const onToggle = jest.fn();
const onFocus = jest.fn();

const buttonTitle = 'button';
const dropdownContent = 'Dropdown content';
function clickOnButton(): void {
    userEvent.click(screen.getByText(buttonTitle));
}

interface TestComponentProps {
    isDisabled?: boolean;
}

const TestComponent = forwardRef<DropdownApi, TestComponentProps>(
    (props: TestComponentProps, ref: ForwardedRef<DropdownApi>): JSX.Element => (
        <Dropdown
            ref={ref}
            {...props}
            buttonProps={{
                size: ButtonSize.S32,
                view: ButtonView.Shade,
                children: buttonTitle,
                onFocus: onFocus,
            }}
            onToggle={onToggle}
        >
            {dropdownContent}
        </Dropdown>
    )
);

const renderDropdown = (isDisabled?: boolean): void => {
    render(<TestComponent isDisabled={isDisabled} />);
};

describe('Dropdown', () => {
    describe('screenshot', () => {
        it('Dropdown', async () => {
            await makeScreenshot(<TestExample />, { width: 400, height: 800 });
        });

        it('disabled', async () => {
            await makeScreenshot(<Disabled />, { width: 400, height: 400 });
        });
    });

    describe('logic', () => {
        beforeEach(() => {
            onToggle.mockClear();
        });

        it('should call onToggle on button click and show dropdown', () => {
            renderDropdown();
            clickOnButton();

            expect(onToggle).toBeCalledWith(true);
            expect(screen.queryAllByText(dropdownContent)).toHaveLength(1);
        });

        it('should close dropdown after esc pressed', () => {
            renderDropdown();
            clickOnButton();

            fireEvent.keyDown(document.activeElement!, { key: 'Esc' });

            expect(onToggle).toHaveBeenLastCalledWith(false);
            expect(screen.queryAllByText(dropdownContent)).toHaveLength(0);
        });

        it('should close dropdown after second click on button', () => {
            renderDropdown();

            // open dropdown
            clickOnButton();

            // second click on button
            clickOnButton();

            expect(onToggle).toHaveBeenLastCalledWith(false);
            expect(screen.queryAllByText(dropdownContent)).toHaveLength(0);
        });

        it('should close dropdown after click outside', () => {
            renderDropdown();
            clickOnButton();

            fireEvent.click(document.body);
            act(() => {
                jest.runAllTimers();
            });

            expect(onToggle).toHaveBeenLastCalledWith(false);
            expect(screen.queryAllByText(dropdownContent)).toHaveLength(0);
        });

        it('should not open dropdown if isDisabled props passed', () => {
            renderDropdown(true);
            clickOnButton();

            expect(onToggle).not.toHaveBeenCalled();
            expect(screen.queryAllByText(dropdownContent)).toHaveLength(0);
        });

        it('should provide correct ref', () => {
            const Component: React.FC = () => {
                const ref = React.useRef<DropdownApi | null>(null);
                const onClick = (): void => {
                    ref.current?.anchor?.focus();
                };

                return (
                    <>
                        <button data-testid="button" onClick={onClick} />
                        <TestComponent ref={ref} />
                    </>
                );
            };
            render(<Component />);
            userEvent.click(screen.getByTestId('button'));
            expect(onFocus).toBeCalled();
        });
    });
});
