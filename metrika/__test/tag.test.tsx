import React from 'react';
import { makeScreenshot } from '@client-libs/test-utils/screenshot';
import { Main, Disabled, Multiline, Caption, WithDot } from '@client-libs/mindstorms/components/tag/tag.stories';
import { Tag } from '../tag';
import userEvent from '@testing-library/user-event';
import { render, screen, fireEvent } from '@testing-library/react';
import { TagView } from '../tag-props';
import { KeyboardKey } from '../../../../keyboard/keyboard-key';
const styles = {
    width: 500,
    height: 500,
};
describe('Tag', () => {
    describe('screenshot', () => {
        it('default', async () => {
            await makeScreenshot(<Main />, styles);
        });
        it('Disabled', async () => {
            await makeScreenshot(<Disabled />, styles);
        });
        it('Multiline', async () => {
            await makeScreenshot(<Multiline />, styles);
        });
        it('Caption', async () => {
            await makeScreenshot(<Caption />, styles);
        });
        it('WithDot', async () => {
            await makeScreenshot(<WithDot />, styles);
        });
    });

    describe('logic', () => {
        const onClickMock = jest.fn();
        const onCloseMock = jest.fn();
        const title = 'Tag';

        function renderTag(props?: { isDisabled?: boolean }): void {
            render(<Tag onClick={onClickMock} onClose={onCloseMock} text={title} view={TagView.Info} {...props} />);
        }

        beforeEach(() => {
            onClickMock.mockClear();
            onCloseMock.mockClear();
        });

        it('should call onClick on tag click', () => {
            renderTag();
            userEvent.click(screen.getByTestId('tag'));

            expect(onClickMock).toBeCalled();
        });

        it('should call onClose on closer click', () => {
            renderTag();
            userEvent.click(screen.getByTestId('tag-closer'));

            expect(onCloseMock).toBeCalled();
        });

        it('should call onClick when Enter pressed', () => {
            renderTag();
            fireEvent.keyDown(screen.getByTestId('tag'), { key: KeyboardKey.Enter });

            expect(onClickMock).toBeCalled();
        });

        it('should call onClick when Space pressed', () => {
            renderTag();
            fireEvent.keyDown(screen.getByTestId('tag'), { key: KeyboardKey.Space });

            expect(onClickMock).toBeCalled();
        });

        it('should call onClose when Enter pressed', () => {
            renderTag();
            fireEvent.keyDown(screen.getByTestId('tag-closer'), { key: KeyboardKey.Enter });

            expect(onCloseMock).toBeCalled();
        });

        it('should call onClose when Space pressed', () => {
            renderTag();
            fireEvent.keyDown(screen.getByTestId('tag-closer'), { key: KeyboardKey.Space });

            expect(onCloseMock).toBeCalled();
        });

        it('should not call onClick if disabled', () => {
            renderTag({ isDisabled: true });
            userEvent.click(screen.getByTestId('tag'));

            expect(onClickMock).not.toBeCalled();
        });

        it('should not call onClick when Enter pressed if disabled', () => {
            renderTag({ isDisabled: true });
            fireEvent.keyDown(screen.getByTestId('tag'), { key: KeyboardKey.Enter });

            expect(onClickMock).not.toBeCalled();
        });
        it('should not call onClick when Space pressed if disabled', () => {
            renderTag({ isDisabled: true });
            fireEvent.keyDown(screen.getByTestId('tag'), { key: KeyboardKey.Space });

            expect(onClickMock).not.toBeCalled();
        });
    });
});
