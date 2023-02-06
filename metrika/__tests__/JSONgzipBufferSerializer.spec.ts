import { expect } from 'chai';
import { taskFork } from '@src/utils/async';
import { noop } from '@src/utils/function';
import { JSONgzipBufferSerializer } from '../JSONgzipBufferSerializer';
import { BufferData } from '../../types';

describe('JSONgzipBufferSerializer', () => {
    it('Synchronously serialize buffer with EOF to JSON', () => {
        const serrializer = new JSONgzipBufferSerializer(window);

        const stubEofEvent = {
            type: 'event',
            data: {
                type: 'eof',
                meta: {},
            },
        };
        const stubEvent = {
            type: 'activity',
            data: '{"field": "value"}',
        };

        const t = serrializer.serialize([
            stubEofEvent,
            stubEvent,
        ] as BufferData[]);
        t(
            taskFork(noop, (result) => {
                expect(result).to.equal(
                    JSON.stringify([
                        {
                            ...stubEofEvent,
                            data: JSON.stringify(stubEofEvent.data),
                        },
                        stubEvent,
                    ]),
                );
            }),
        );
    });
});
