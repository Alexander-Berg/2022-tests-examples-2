import React, { FC, useRef } from 'react';

import { makeScreenshot } from '@client-libs/test-utils/screenshot';
import { TestContext } from '@client-libs/mindstorms/service/test-context/test-context';

import { ButtonSize, ButtonView } from '../../button/button-props';
import { Button } from '../../button/button';

import { Axis, InversedAxisType } from '../../popup/popup-props';
import { SvgIconSize } from '../../icon/svg-icon-size';
import { QuestionIcon } from '../../icon/question-icon';

import { Tooltip, tooltipClassName } from '../tooltip';
import { TooltipProps, TooltipSize, TooltipToggleMode, TooltipView } from '../tooltip-props';
import { SmartTooltip } from '../smart-tooltip';

import { render, RenderResult } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

const defaultProps = {
    isVisible: true,
    anchorPosition: {
        mainAxis: Axis.Right,
        inversedAxis: InversedAxisType.Center,
    },
    anchorTarget: { current: null },
    view: TooltipView.Dark,
    size: TooltipSize.S,
    title: 'Tooltip',
    description: 'Some description',
    icon: <QuestionIcon size={SvgIconSize.S24} />,
    withClose: true,
    hasTail: true,
};

const ScreenshotExample: FC<Partial<TooltipProps>> = props => {
    const anchorTarget = useRef(null);

    return (
        <TestContext.Provider value={true}>
            <div style={{ position: 'absolute', margin: 40 }}>
                <div ref={anchorTarget} />
                <Tooltip {...defaultProps} {...props} anchorTarget={anchorTarget} />
            </div>
        </TestContext.Provider>
    );
};

const SmartTooltipExample: FC<{ toggleMode: TooltipToggleMode }> = props => {
    const { toggleMode } = props;
    const anchorTarget = useRef(null);

    return (
        <>
            <h1>Outside content</h1>

            <Button ref={anchorTarget} size={ButtonSize.S36} view={ButtonView.Shade}>
                Button
            </Button>

            <SmartTooltip {...defaultProps} anchorTarget={anchorTarget} toggleMode={toggleMode} />
        </>
    );
};

describe('Tooltip', () => {
    describe('screenshot', () => {
        const options = { width: 300, height: 140 };

        it('tail', async () => {
            [Axis.Top, Axis.Right, Axis.Bottom, Axis.Left].forEach(async mainAxis => {
                const anchorPosition = { mainAxis, inversedAxis: InversedAxisType.Center };
                await makeScreenshot(<ScreenshotExample anchorPosition={anchorPosition} />, options);
            });
        });

        it('without tail', async () => {
            await makeScreenshot(<ScreenshotExample hasTail={false} />, options);
        });

        it('without close', async () => {
            await makeScreenshot(<ScreenshotExample withClose={false} />, options);
        });

        it('only title', async () => {
            await makeScreenshot(<ScreenshotExample description={undefined} icon={undefined} />, options);
        });

        it('only title and icon', async () => {
            await makeScreenshot(<ScreenshotExample description={undefined} />, options);
        });

        it('only title and description', async () => {
            await makeScreenshot(<ScreenshotExample icon={undefined} />, options);
        });
    });

    describe('smart tooltip logic', () => {
        const onButtonClick = jest.fn();

        beforeEach(() => {
            onButtonClick.mockClear();
        });

        const getOutsideContent = (elem: Element): HTMLElement => elem.querySelector('h1')!;
        const getTooltipAnchor = (elem: Element): HTMLElement => elem.querySelector('button')!;
        const getTooltip = (elem: Element): HTMLElement => elem.querySelector(`.${tooltipClassName}`)!;
        const getClose = (elem: Element): HTMLElement => elem.querySelector(`.${tooltipClassName}__close-icon`)!;

        describe('click', () => {
            const renderTooltip = (): RenderResult =>
                render(<SmartTooltipExample toggleMode={TooltipToggleMode.Click} />);

            it('should be shown by click', () => {
                const { baseElement } = renderTooltip();

                userEvent.click(getTooltipAnchor(baseElement));

                expect(getTooltip(baseElement)).not.toBe(null);
            });

            it('should be closed after second click to the anchor', () => {
                const { baseElement } = renderTooltip();

                userEvent.click(getTooltipAnchor(baseElement));
                userEvent.click(getTooltipAnchor(baseElement));

                expect(getTooltip(baseElement)).toBe(null);
            });

            it('should be closed after close icon click', () => {
                const { baseElement } = renderTooltip();

                userEvent.click(getTooltipAnchor(baseElement));
                userEvent.click(getClose(baseElement));

                expect(getTooltip(baseElement)).toBe(null);
            });
        });

        describe('hover', () => {
            const renderTooltip = (): RenderResult =>
                render(<SmartTooltipExample toggleMode={TooltipToggleMode.Hover} />);

            it('should be shown by hover', () => {
                const { baseElement } = renderTooltip();

                userEvent.hover(getTooltipAnchor(baseElement));

                expect(getTooltip(baseElement)).not.toBe(null);
            });

            it('should be closed after hover to the outside content', () => {
                const { baseElement } = renderTooltip();

                userEvent.hover(getTooltipAnchor(baseElement));
                userEvent.hover(getOutsideContent(baseElement));

                expect(getTooltip(baseElement)).toBe(null);
            });
        });
    });
});
