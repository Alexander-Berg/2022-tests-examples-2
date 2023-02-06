import * as chai from 'chai';
import { getCollectActivityCallbacks } from '../collectActivity';

describe('collect activity', () => {
    it('collects activity', () => {
        const { onEventPush, aggregate } = getCollectActivityCallbacks();
        const result: any = aggregate([]);
        const notRelevantEvent: any = {
            data: {
                type: 'not_relevant_event',
            },
        };
        onEventPush(notRelevantEvent);
        chai.expect(result, 'no aggregation for empty array').to.not.be.ok;
        chai.expect({ type: 'activity', data: 0 }).to.deep.equal(
            aggregate([notRelevantEvent]),
        );

        const relevantEvent: any = {
            data: {
                type: 'change',
            },
        };
        onEventPush(relevantEvent);
        chai.expect({ type: 'activity', data: 65 }).to.deep.equal(
            aggregate([relevantEvent]),
        );
    });
});
