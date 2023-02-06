import * as chai from 'chai';
import {
    GDPR_ENABLE_ALL,
    GDPR_OK_VIEW_DEFAULT,
    GDPR_OK_VIEW_DETAILED,
    GDPR_VALID_VALUES,
    parseGdprValue,
} from '@src/middleware/gdpr/status';

describe('gdpr status', () => {
    it('parseGdprValue', () => {
        chai.expect(parseGdprValue(GDPR_OK_VIEW_DEFAULT)).to.eq(
            GDPR_ENABLE_ALL,
        );
        chai.expect(parseGdprValue(GDPR_OK_VIEW_DETAILED)).to.eq(
            GDPR_ENABLE_ALL,
        );
        [0, 1, 2, 3].map((item) =>
            chai
                .expect(parseGdprValue(`${GDPR_OK_VIEW_DETAILED}-${item}`))
                .to.eq(GDPR_VALID_VALUES[item]),
        );

        chai.expect(parseGdprValue('nonexistent')).to.eq(GDPR_ENABLE_ALL);
    });
});
