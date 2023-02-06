import * as React from 'react';

import { makeScreenshot } from '@client-libs/test-utils/screenshot';
import { Axis, InversedAxisType } from '../popup-props';
import { TestExample } from '../popup.stories';
import { calculatePosition } from '../position';

const anchorRect: DOMRect = {
    bottom: 368,
    height: 252,
    left: 265,
    right: 767,
    top: 116,
    width: 502,
    x: 265,
    y: 116,
    toJSON: () => null,
};

const popups = [
    {
        anchorPosition: {
            mainAxis: Axis.Top,
            inversedAxis: InversedAxisType.Start,
        },
        rect: {
            bottom: 106,
            height: 39,
            left: 265,
            right: 369.46875,
            top: 67,
            width: 104.46875,
            x: 265,
            y: 67,
        },
    },
    {
        anchorPosition: {
            mainAxis: Axis.Top,
            inversedAxis: InversedAxisType.Center,
        },
        rect: {
            bottom: 106,
            height: 39,
            left: 457,
            right: 573.375,
            top: 67,
            width: 116.375,
            x: 457,
            y: 67,
        },
    },
    {
        anchorPosition: {
            mainAxis: Axis.Top,
            inversedAxis: InversedAxisType.End,
        },
        rect: {
            bottom: 106,
            height: 39,
            left: 669.015625,
            right: 767,
            top: 67,
            width: 97.984375,
            x: 669.015625,
            y: 67,
        },
    },
    {
        anchorPosition: {
            mainAxis: Axis.Bottom,
            inversedAxis: InversedAxisType.Start,
        },
        rect: {
            bottom: 417,
            height: 39,
            left: 265,
            right: 398.515625,
            top: 378,
            width: 133.515625,
            x: 265,
            y: 378,
        },
    },
    {
        anchorPosition: {
            mainAxis: Axis.Bottom,
            inversedAxis: InversedAxisType.Center,
        },
        rect: {
            bottom: 417,
            height: 39,
            left: 443,
            right: 588.421875,
            top: 378,
            width: 145.421875,
            x: 443,
            y: 378,
        },
    },
    {
        anchorPosition: {
            mainAxis: Axis.Bottom,
            inversedAxis: InversedAxisType.End,
        },
        rect: {
            bottom: 417,
            height: 39,
            left: 639.96875,
            right: 767,
            top: 378,
            width: 127.03125,
            x: 639.96875,
            y: 378,
        },
    },
    {
        anchorPosition: {
            mainAxis: Axis.Left,
            inversedAxis: InversedAxisType.Start,
        },
        rect: {
            bottom: 155,
            height: 39,
            left: 151.484375,
            right: 255,
            top: 116,
            width: 103.515625,
            x: 151.484375,
            y: 116,
        },
    },
    {
        anchorPosition: {
            mainAxis: Axis.Left,
            inversedAxis: InversedAxisType.Center,
        },
        rect: {
            bottom: 261,
            height: 39,
            left: 139.578125,
            right: 255,
            top: 222,
            width: 115.421875,
            x: 139.578125,
            y: 222,
        },
    },
    {
        anchorPosition: {
            mainAxis: Axis.Left,
            inversedAxis: InversedAxisType.End,
        },
        rect: {
            bottom: 368,
            height: 39,
            left: 157.96875,
            right: 255,
            top: 329,
            width: 97.03125,
            x: 157.96875,
            y: 329,
        },
    },
    {
        anchorPosition: {
            mainAxis: Axis.Right,
            inversedAxis: InversedAxisType.Start,
        },
        rect: {
            bottom: 155,
            height: 39,
            left: 777,
            right: 890.609375,
            top: 116,
            width: 113.609375,
            x: 777,
            y: 116,
        },
    },
    {
        anchorPosition: {
            mainAxis: Axis.Right,
            inversedAxis: InversedAxisType.Center,
        },
        rect: {
            bottom: 261,
            height: 39,
            left: 777,
            right: 902.515625,
            top: 222,
            width: 125.515625,
            x: 777,
            y: 222,
        },
    },
    {
        anchorPosition: {
            mainAxis: Axis.Right,
            inversedAxis: InversedAxisType.End,
        },
        rect: {
            bottom: 368,
            height: 39,
            left: 777,
            right: 884.125,
            top: 329,
            width: 107.125,
            x: 777,
            y: 329,
        },
    },
];

describe('Popup', () => {
    describe('screenshot', () => {
        it('view', async () => {
            await makeScreenshot(<TestExample />, { width: 400, height: 400 });
        });
    });

    describe.each(popups)('direction', popup =>
        it(`calc position ${popup.anchorPosition.mainAxis}-${popup.anchorPosition.inversedAxis}`, () => {
            const position = calculatePosition({
                anchorPosition: popup.anchorPosition,
                anchorRect,
                popupRect: { ...popup.rect, toJSON: (): null => null },
                visibleContainerRect: new DOMRect(0, 0, 1000, 1000),
                renderContainerRect: new DOMRect(0, 0, 1000, 1000),
            });
            expect(position.position).toMatchObject({
                top: popup.rect.top,
                left: popup.rect.left,
            });
        })
    );
});
