import * as React from 'react';

import { makeScreenshot } from '@client-libs/test-utils/screenshot';

import { TestExample } from '../promo-wizard.stories';
import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PromoWizardProps } from '../promo-wizard-props';
import { KeyboardKey } from '@client-libs/keyboard/keyboard-key';

function renderWizard(props?: Partial<PromoWizardProps>): void {
    render(<TestExample onChangeStep={onChangeStep} onComplete={onComplete} {...props} />);
}

const onChangeStep = jest.fn();
const onComplete = jest.fn();

describe('PromoWizard', () => {
    describe('screenshot', () => {
        it('step 0', async () => {
            await makeScreenshot(<TestExample />, { width: 750, height: 300 });
        });
        it('step 1', async () => {
            await makeScreenshot(<TestExample currentStep={1} />, { width: 750, height: 300 });
        });
    });
    describe('logic', () => {
        beforeEach(() => {
            onChangeStep.mockClear();
            onComplete.mockClear();
        });

        it('should show next slide on click', () => {
            renderWizard();
            userEvent.click(screen.getByTestId('nextButton'));
            expect(onChangeStep).toBeCalledWith(0, 1);
        });

        it('should show next slide on arrow right', () => {
            renderWizard();
            fireEvent.keyDown(document, { key: KeyboardKey.ArrowRight });
            expect(onChangeStep).toBeCalledWith(0, 1);
        });

        it('should show previous slide', () => {
            renderWizard({ currentStep: 1 });
            userEvent.click(screen.getByTestId('prevButton'));
            expect(onChangeStep).toBeCalledWith(1, 0);
        });

        it('should show previous slide on arrow left', () => {
            renderWizard({ currentStep: 1 });
            fireEvent.keyDown(document, { key: KeyboardKey.ArrowLeft });
            expect(onChangeStep).toBeCalledWith(1, 0);
        });

        it('should call onComplete when on last slide', () => {
            renderWizard({ currentStep: 3 });
            userEvent.click(screen.getByTestId('nextButton'));
            expect(onComplete).toBeCalled();
        });

        it('should switch steps when clicking on points', () => {
            renderWizard();
            userEvent.click(screen.getByTestId('step-point-2'));
            expect(onChangeStep).toBeCalledWith(0, 2);
        });
    });
});
