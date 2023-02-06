import * as chai from 'chai';
import { hasPublisherData } from '../hasPublisherData';

describe('hasPublisherData', () => {
    it('finds publisher data', () => {
        chai.assert(
            hasPublisherData([
                {
                    type: 'event',
                },
                {
                    type: 'mutation',
                },
                {
                    type: 'publishersHeader',
                },
            ] as any),
        );
    });
    it('ignores other data', () => {
        chai.assert(
            !hasPublisherData([
                {
                    type: 'mutation',
                },
                {
                    type: 'event',
                },
            ] as any),
        );
    });
});
