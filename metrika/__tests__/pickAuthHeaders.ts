import { Request } from 'express';
import { pickAuthHeaders } from '../pickAuthHeaders';

describe('pickAuthHeaders', () => {
    it('works', () => {
        const req = ({
            tvm: {
                tickets: {
                    api: { ticket: 'q' },
                },
            },
            blackbox: {
                userTicket: 'a',
            },
        } as any) as Request;

        expect(pickAuthHeaders(req, 'api')).toMatchSnapshot();
    });
    it('works without required fields', () => {
        const req = ({} as any) as Request;

        expect(pickAuthHeaders(req, 'no-matter')).toMatchSnapshot();
    });
    it('omit empty values', () => {
        const req = ({
            tvm: {
                tickets: {
                    api: { ticket: null },
                },
            },
            blackbox: {
                userTicket: undefined,
            },
        } as any) as Request;

        expect(pickAuthHeaders(req, 'api')).toMatchSnapshot();
    });
});
