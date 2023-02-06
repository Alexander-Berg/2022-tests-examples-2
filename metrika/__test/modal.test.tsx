import React from 'react';
import { makeScreenshot } from '@client-libs/test-utils/screenshot';
import { CustomOverlay, TestExample } from '@client-libs/mindstorms/components/modal/modal.stories';
import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Modal } from '@client-libs/mindstorms/components/modal/modal';
import { ModalProps } from '@client-libs/mindstorms/components/modal/modal-props';
import { TestContext } from '@client-libs/mindstorms/service/test-context/test-context';

const onClose = jest.fn();

function renderModal(props?: Partial<ModalProps>): void {
    render(
        <TestContext.Provider value={true}>
            <Modal isVisible onClose={onClose} {...props}>
                modal content
            </Modal>
        </TestContext.Provider>
    );
}

describe('Modal', () => {
    describe('screenshot', () => {
        it('default', async () => {
            await makeScreenshot(<TestExample />, { width: 800, height: 400 });
        });

        it('high', async () => {
            await makeScreenshot(<TestExample isHigh />, { width: 800, height: 400 });
        });

        it('custom overlay', async () => {
            await makeScreenshot(<CustomOverlay />, { width: 800, height: 400 });
        });
    });

    describe('logic', () => {
        beforeEach(() => {
            onClose.mockClear();
        });

        it('should close modal by click cross', () => {
            renderModal();
            userEvent.click(screen.getByTestId('modal-cross'));
            expect(onClose).toBeCalled();
        });

        it('should close modal by press escape', () => {
            renderModal();
            fireEvent.keyDown(document, { key: 'Esc' });
            expect(onClose).toBeCalled();
        });

        it('shouldn`t close modal by by press escape when shouldCloseOnClickOutside is false', () => {
            renderModal({ shouldCloseOnClickOutside: false });
            fireEvent.keyDown(document, { key: 'Esc' });
            expect(onClose).not.toBeCalled();
        });

        it('should close modal by click outside', () => {
            renderModal();
            userEvent.click(screen.getByTestId('modal-overlay'));
            expect(onClose).toBeCalled();
        });

        it('shouldn`t close modal by click outside when shouldCloseOnClickOutside is false', () => {
            renderModal({ shouldCloseOnClickOutside: false });
            userEvent.click(screen.getByTestId('modal-overlay'));
            expect(onClose).not.toBeCalled();
        });
    });
});
