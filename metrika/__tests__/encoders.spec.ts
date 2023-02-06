import { ELEMENT_ID_PROPERTY } from '@private/src/providers/formvisor/global';
import { assertByteCode } from '@private/src/providers/formvisor/__tests__/common';
import {
    encodeEOF,
    encodeResize,
    encodeScroll,
    encodeScrollLocal,
    encodeWheelEvent,
} from '../encoders';

describe('webvisor encoders: ', () => {
    let win: Window;

    beforeEach(() => {
        win = {
            document: {},
        } as any as Window;
    });

    it('encodeScroll', () => {
        const coordinates = { x: 100, y: 100 };
        assertByteCode(encodeScroll(1000, coordinates), [3, 232, 7, 100, 100]);
    });

    it('encodeScrollLocal', () => {
        const coordinates = { x: 100, y: 100 };
        const el = { [ELEMENT_ID_PROPERTY]: 1 } as any as HTMLElement;
        assertByteCode(
            encodeScrollLocal(1000, coordinates, el),
            // prettier-ignore
            [ 16, 232, 7, 100, 100, 1 ],
        );
    });

    it('encodeEOF', () => {
        assertByteCode(encodeEOF(win), [13]);
    });

    it('encodeResize', () => {
        const winSize = [400, 400];
        const docSize = [500, 500];
        assertByteCode(
            encodeResize(
                1000,
                winSize as [number, number],
                docSize as [number, number],
            ),
            // prettier-ignore
            [28, 232, 7, 144, 3, 144, 3, 244, 3, 244, 3],
        );
    });

    it('encodeWheelEvent', () => {
        const el = { [ELEMENT_ID_PROPERTY]: 1 } as any as HTMLElement;
        const pos = [100, 100] as [number, number];
        assertByteCode(
            encodeWheelEvent(1000, el, pos, 1),
            // prettier-ignore
            [31, 232, 7, 1, 100, 100, 0, 0, 1],
        );
    });
});
