/* eslint-env mocha */
import * as chai from 'chai';
import { isSafariVersion } from '@src/middleware/crossDomain/utils';

describe('crossDomain utils', () => {
    it('isSafariVersion', () => {
        chai.expect(
            isSafariVersion(
                {
                    navigator: {
                        vendor: 'Apple Computer, Inc.',
                        userAgent:
                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15',
                    } as any,
                } as any,
                '14.1',
            ),
        ).to.be.false;

        chai.expect(
            isSafariVersion(
                {
                    navigator: {
                        vendor: 'Apple Computer, Inc.',
                        userAgent:
                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Safari/605.1.15',
                    } as any,
                } as any,
                '14.1',
            ),
        ).to.be.false;

        chai.expect(
            isSafariVersion(
                {
                    navigator: {
                        vendor: 'Apple Computer, Inc.',
                        userAgent:
                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
                    } as any,
                } as any,
                '14.1',
            ),
        ).to.be.false;

        chai.expect(
            isSafariVersion(
                {
                    navigator: {
                        vendor: 'Apple Computer, Inc.',
                        userAgent:
                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15',
                    } as any,
                } as any,
                '14.1',
            ),
        ).to.be.true;
    });
});
