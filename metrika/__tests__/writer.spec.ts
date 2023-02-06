/* eslint camelcase: 0 */
import {
    encodeEvent,
    encodeMouseEvent,
    encodeTouchEvent,
} from '@generated/proto/events';
import { encodePage, encodePage_Content } from '@generated/proto/pages';
import {
    encodeBuffer,
    encodeBufferWrapper,
} from '@generated/proto/recorder_proto';
import { expect } from 'chai';
import { noopOp, SizeCalculator } from '../const';
import { encode_string, encode_uint32 } from '../primitive';
import {
    forkOperation,
    HEAD_INDEX_SIZE,
    LEN_INDEX_OP,
    LEN_INDEX_SIZE,
    NEXT_INDEX_OP,
    OPERATION_INDEX_OP,
    pushOperaton,
    squashToLenghtOperation,
    syncWriter,
    VALUE_INDEX_OP,
} from '../writer';

const touchesJS = [
    {
        id: 'adfads1023',
        x: 10.091,
        y: 10.75,
        force: 123.102,
    },
    {
        id: 'rtlwwq',
        x: 5790.123,
        y: -678.443,
        force: -203.012,
    },
];
const touchesBytes = [
    // repeted
    10, 27,
    // string 'adfads1023' - 12
    10, 10, 97, 100, 102, 97, 100, 115, 49, 48, 50, 51,
    // float x '10.091' - 5 + 12 = 17
    21, 188, 116, 33, 65,
    // float y - 5 + 17 = 22
    29, 0, 0, 44, 65,
    // float force - 5 + 22 = 27
    37, 57, 52, 246, 66,
    // repeated
    10, 23,
    // string
    10, 6, 114, 116, 108, 119, 119, 113,
    // float
    21, 252, 240, 180, 69,
    // float
    29, 90, 156, 41, 196,
    // / float
    37, 18, 3, 75, 195,
];

describe('bufferWriter', () => {
    const win = {
        // eslint-disable-next-line no-restricted-globals
        isNaN,
        Uint8Array,
        Math,
    } as any;
    beforeEach(() => {});
    it('write primitve values', () => {
        let data = syncWriter(win, encodeMouseEvent, {
            x: 1,
            y: 2,
        });
        expect(Array.from(data)).to.be.deep.eq([8, 1, 16, 2]);
        data = syncWriter(win, encodeMouseEvent, {
            x: 11231,
            y: 99324112,
        });
        expect(Array.from(data)).to.be.deep.eq([
            8, 223, 87, 16, 208, 161, 174, 47,
        ]);
    });
    it('does squash and push operations', () => {
        const startOp = noopOp();
        const curentState: SizeCalculator = [0, startOp, startOp];

        pushOperaton(curentState, encode_uint32(9));
        forkOperation(curentState);
        pushOperaton(curentState, encode_uint32(10));
        pushOperaton(curentState, encode_string('1234'));
        squashToLenghtOperation(curentState);
        pushOperaton(curentState, encode_uint32(9));
        forkOperation(curentState);
        pushOperaton(curentState, encode_uint32(10));
        pushOperaton(curentState, encode_string('1234'));
        squashToLenghtOperation(curentState);
        let head = curentState[HEAD_INDEX_SIZE][NEXT_INDEX_OP];
        let cursor = 0;
        const buffer = new Array(curentState[LEN_INDEX_SIZE]);
        while (head) {
            head[OPERATION_INDEX_OP](
                {} as any,
                head[VALUE_INDEX_OP],
                buffer,
                cursor,
            );
            cursor += head[LEN_INDEX_OP];
            head = head[NEXT_INDEX_OP];
        }
        expect(buffer).to.be.deep.eq([
            9, 5, 10, 49, 50, 51, 52, 9, 5, 10, 49, 50, 51, 52,
        ]);
    });
    it('write custom repeated values', () => {
        const data = syncWriter(win, encodeTouchEvent, {
            touches: touchesJS,
        });
        expect(Array.from(data)).to.be.deep.eq(touchesBytes);
    });
    it('writes map types', () => {
        const data = syncWriter(win, encodePage_Content, {
            id: 1003,
            name: 'page',
            attributes: {
                a: '123',
                b: '456',
            },
            hidden: true,
        });
        expect(Array.from(data)).to.be.deep.eq([
            8, 235, 7, 18, 4, 112, 97, 103, 101, 26, 8, 10, 1, 97, 18, 3, 49,
            50, 51, 26, 8, 10, 1, 98, 18, 3, 52, 53, 54, 64, 1,
        ]);
    });
    it('writes int64', () => {
        const data = syncWriter(win, encodePage, {
            recordStamp: 10023,
            tabId: '123123',
        });
        expect(Array.from(data)).to.be.deep.eq([
            34, 6, 49, 50, 51, 49, 50, 51, 40, 167, 78,
        ]);
    });
    it('writes sint32', () => {
        const data = syncWriter(win, encodeEvent, {
            target: 1346,
            touchEvent: {
                touches: touchesJS,
            },
        });
        expect(Array.from(data)).to.be.deep.eq([
            16,
            132,
            21,
            74,
            54,
            ...touchesBytes,
        ]);
    });
    it('writes negatives', () => {
        const data = syncWriter(win, encodeMouseEvent, {
            x: -134,
            y: 253,
        });
        expect(Array.from(data)).to.be.deep.eq([
            8, 250, 254, 255, 255, 255, 255, 255, 255, 255, 1, 16, 253, 1,
        ]);
    });
    it('writes bytes', () => {
        const data = syncWriter(win, encodeBuffer, {
            stamp: 1002,
            page: 0,
            end: true,
            chunk: [1, 2, 3, 1, 2, 3, 4],
        });
        expect(Array.from(data)).to.be.deep.eq([
            8, 234, 7, 24, 0, 34, 7, 1, 2, 3, 1, 2, 3, 4, 40, 1,
        ]);
    });
    it('writes enum types', () => {
        const data = syncWriter(win, encodeEvent, {
            type: 15,
            touchEvent: {
                touches: touchesJS,
            },
        });
        expect(Array.from(data)).to.be.deep.eq([
            8,
            15,
            74,
            54,
            ...touchesBytes,
        ]);
    });
    it('writes sub types', () => {
        const data = syncWriter(win, encodeEvent, {
            touchEvent: {
                touches: touchesJS,
            },
        });
        expect(Array.from(data)).to.be.deep.eq([74, 54, ...touchesBytes]);
    });
    it('write complex message', () => {
        const data = syncWriter(win, encodeBufferWrapper, {
            buffer: [
                {
                    stamp: 100,
                    data: {
                        mutation: {
                            stamp: 10,
                            meta: {
                                changes: [
                                    {
                                        c: [
                                            {
                                                id: 57,
                                                at: {
                                                    class: {
                                                        o: 'old',
                                                        n: 'new',
                                                        r: true,
                                                    },
                                                },
                                            },
                                        ],
                                    },
                                ],
                            },
                        },
                    },
                },
            ],
        });
        expect(Array.from(data)).to.be.deep.eq([
            10, 39, 8, 100, 18, 35, 18, 33, 16, 10, 26, 29, 18, 27, 26, 25, 8,
            57, 18, 21, 10, 5, 99, 108, 97, 115, 115, 18, 12, 10, 3, 111, 108,
            100, 18, 3, 110, 101, 119, 24, 1,
        ]);
    });
});
