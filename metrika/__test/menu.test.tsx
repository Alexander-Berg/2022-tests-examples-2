import { makeScreenshot } from '@client-libs/test-utils/screenshot';
import * as React from 'react';
import {
    MenuItemWithNestedTestExample,
    MenuSwitchItem,
    MenuValueItem,
} from '@client-libs/mindstorms/components/menu/menu.stories';
import { renderHook, RenderResult, act } from '@testing-library/react-hooks';
import {
    UseKeyboardMenuNavigation,
    useKeyboardMenuNavigation,
} from '@client-libs/mindstorms/components/menu/use-keyboard-menu-navigation';
import { KeyboardKey } from '@client-libs/keyboard/keyboard-key';
import { fireEvent, render, screen } from '@testing-library/react';
import {
    Menu,
    MenuItemWithNested as MenuItemWithNestedComponent,
    MenuSwitchItem as MenuRadioItemComponent,
    MenuValueItem as MenuValueItemComponent,
} from '@client-libs/mindstorms/components/menu/menu';
import '@testing-library/jest-dom/extend-expect';
import { MenuItem } from '@client-libs/mindstorms/components/menu/menu-props';

const items = [1, 2, 3];
const initialPosition = 1;

const onRadioChange = jest.fn();
const onSelect = jest.fn();
const onEnter = jest.fn();
const onSpace = jest.fn();
const onEscape = jest.fn();
const onArrowLeft = jest.fn();
const onArrowRight = jest.fn();

function emulateKeyDown(key: KeyboardKey): void {
    act(() => {
        fireEvent.keyDown(document, { key });
    });
}

const itemWithNestedTitle = 'Данные';
const radioItemTitle = 'Рекомендации и новости';
const valueItemTitle = 'С роботами';
const nestedContent = 'Nested content';

const menuItems: MenuItem[] = [
    {
        content: <MenuItemWithNestedComponent title={itemWithNestedTitle} />,
        nested: <div>{nestedContent}</div>,
    },
    {
        content: <MenuRadioItemComponent title={radioItemTitle} onChange={onRadioChange} isChecked={false} />,
    },
    {
        content: (
            <MenuValueItemComponent
                id="withRobots"
                key="withRobots"
                isSelected={false}
                title={valueItemTitle}
                onSelect={onSelect}
            />
        ),
    },
];

function renderMenu(): void {
    render(<Menu minWidth={300} items={menuItems} />);
}

describe('Menu', () => {
    describe('screenshot', () => {
        it('MenuValueItem', async () => {
            await makeScreenshot(<MenuValueItem />, { width: 300, height: 100 });
        });

        it('MenuSwitchItem', async () => {
            await makeScreenshot(<MenuSwitchItem />, { width: 300, height: 100 });
        });

        it('MenuItemWithNested', async () => {
            await makeScreenshot(<MenuItemWithNestedTestExample />, { width: 300, height: 100 });
        });
    });

    describe('logic', () => {
        beforeEach(() => {
            jest.useFakeTimers();
        });

        it('should show nested content while hovering on item', () => {
            renderMenu();
            emulateKeyDown(KeyboardKey.Down);
            emulateKeyDown(KeyboardKey.ArrowRight);

            expect(screen.queryByText(nestedContent)).toBeInTheDocument();
        });

        it('should call onSelect from MenuValueItem on enter', () => {
            renderMenu();
            emulateKeyDown(KeyboardKey.Down);
            emulateKeyDown(KeyboardKey.Down);
            emulateKeyDown(KeyboardKey.Enter);
            expect(onRadioChange).toBeCalledWith(true);
        });

        it('should call onSelect from MenuValueItem on enter', () => {
            renderMenu();
            emulateKeyDown(KeyboardKey.Down);
            emulateKeyDown(KeyboardKey.Down);
            emulateKeyDown(KeyboardKey.Down);
            emulateKeyDown(KeyboardKey.Enter);
            expect(onSelect).toBeCalled();
        });
    });
});

function renderUseKeyboardNavigation(): RenderResult<UseKeyboardMenuNavigation> {
    const { result } = renderHook(() =>
        useKeyboardMenuNavigation({
            items: menuItems,
            initialPosition,
            isDisabled: false,
            onEnter,
            onSpace,
            onEscape,
            onArrowRight,
            onArrowLeft,
        })
    );
    return result;
}

describe('useKeyboardMenuNavigation', () => {
    beforeEach(() => {
        onEnter.mockClear();
        onSpace.mockClear();
        onEscape.mockClear();
        onArrowRight.mockClear();
        onArrowLeft.mockClear();
    });

    describe('navigation', () => {
        beforeEach(() => {
            renderUseKeyboardNavigation();
        });

        it('should navigate to next item by keyDown and call onEnter', () => {
            emulateKeyDown(KeyboardKey.ArrowDown);
            emulateKeyDown(KeyboardKey.Enter);
            expect(onEnter).toBeCalledWith(initialPosition + 1);
        });

        it('should navigate to previous item by keyUp and call onEnter', () => {
            emulateKeyDown(KeyboardKey.Up);
            emulateKeyDown(KeyboardKey.Enter);
            expect(onEnter).toBeCalledWith(initialPosition - 1);
        });

        it('should navigate to the first item on Down-key from the last item ', () => {
            for (let i = initialPosition; i < items.length; i++) {
                emulateKeyDown(KeyboardKey.Down);
            }
            emulateKeyDown(KeyboardKey.Enter);
            expect(onEnter).toBeCalledWith(0);
        });

        it('should navigate to the last item on Up-key from the first element', () => {
            for (let i = initialPosition; i > -1; i--) {
                emulateKeyDown(KeyboardKey.Up);
            }
            emulateKeyDown(KeyboardKey.Enter);
            expect(onEnter).toBeCalledWith(items.length - 1);
        });

        it('should call onArrowRight', () => {
            emulateKeyDown(KeyboardKey.ArrowRight);
            expect(onArrowRight).toBeCalled();
        });

        it('should call onArrowLeft', () => {
            emulateKeyDown(KeyboardKey.ArrowLeft);
            expect(onArrowLeft).toBeCalled();
        });

        it('should call onEscape', () => {
            emulateKeyDown(KeyboardKey.Escape);
            expect(onEscape).toBeCalledWith(initialPosition);
        });

        it('should call onSpace', () => {
            emulateKeyDown(KeyboardKey.Space);
            expect(onSpace).toBeCalledWith(initialPosition);
        });
    });
});
