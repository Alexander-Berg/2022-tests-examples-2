import { fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import {
    UseKeyboardListNavigation,
    useKeyboardListNavigation,
} from '@client-libs/keyboard/use-keyboard-list-navigation';
import { KeyboardKey } from '@client-libs/keyboard/keyboard-key';
import { renderHook, RenderResult, act } from '@testing-library/react-hooks';

const items = [1, 2, 3];
const initialPosition = 1;
const focusedElement = document.activeElement!;

function emulateKeyDown(key: KeyboardKey): void {
    act(() => {
        fireEvent.keyDown(focusedElement, { key });
    });
}

const onEnter = jest.fn();
const onSpace = jest.fn();
const onEscape = jest.fn();

function renderUseKeyboardNavigation(isDisabled: boolean): RenderResult<UseKeyboardListNavigation> {
    const { result } = renderHook(() =>
        useKeyboardListNavigation({
            itemsLength: items.length,
            initialPosition,
            isDisabled,
            onEnter,
            onSpace,
            onEscape,
        })
    );
    return result;
}

describe('useKeyboardListNavigation', () => {
    beforeEach(() => {
        onEnter.mockClear();
        onSpace.mockClear();
        onEscape.mockClear();
    });

    describe('navigation', () => {
        beforeEach(() => {
            renderUseKeyboardNavigation(false);
        });

        it('should move to the element with the `down` key and call onEnter by pressing enter', () => {
            emulateKeyDown(KeyboardKey.Down);
            emulateKeyDown(KeyboardKey.Enter);
            expect(onEnter).toBeCalledWith(initialPosition + 1);
        });

        it('should move to the element with the `up` key and call onEnter by pressing enter', () => {
            emulateKeyDown(KeyboardKey.Up);
            emulateKeyDown(KeyboardKey.Enter);
            expect(onEnter).toBeCalledWith(initialPosition - 1);
        });

        it('should move to the first element with the `down` key after last element', () => {
            for (let i = initialPosition; i < items.length; i++) {
                emulateKeyDown(KeyboardKey.Down);
            }
            emulateKeyDown(KeyboardKey.Enter);
            expect(onEnter).toBeCalledWith(0);
        });

        it('should move to the last element with the `up` key after first element', () => {
            for (let i = initialPosition; i > -1; i--) {
                emulateKeyDown(KeyboardKey.Up);
            }
            emulateKeyDown(KeyboardKey.Enter);
            expect(onEnter).toBeCalledWith(items.length - 1);
        });

        it('should call onEscape by pressing escape', () => {
            emulateKeyDown(KeyboardKey.Escape);
            expect(onEscape).toBeCalledWith(initialPosition);
        });

        it('should call onEscape by pressing esc', () => {
            emulateKeyDown(KeyboardKey.Esc);
            expect(onEscape).toBeCalledWith(initialPosition);
        });

        it('should call onSpace by pressing space', () => {
            emulateKeyDown(KeyboardKey.Space);
            expect(onSpace).toBeCalledWith(initialPosition);
        });
    });

    describe('change current position', () => {
        it('should change item position by call setCurrentPosition', () => {
            const result = renderUseKeyboardNavigation(false);
            const index = 2;
            act(() => {
                result.current.setCurrentPosition(index);
            });
            expect(result.current.currentPosition).toBe(index);
        });
    });

    describe('without navigation', () => {
        beforeEach(() => {
            renderUseKeyboardNavigation(true);
        });

        it('shouldn`t move to the element with the arrow key', () => {
            emulateKeyDown(KeyboardKey.Down);
            emulateKeyDown(KeyboardKey.Enter);
            expect(onEnter).not.toBeCalled();
        });
    });
});
