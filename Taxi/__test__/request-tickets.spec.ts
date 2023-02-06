import {Request} from 'express';

process.env.CFG_DIR = 'node-config';

test('requestTickets cache', async () => {
    const {default: requestTickets} = await import('../request-tickets');

    const req1: Request = {} as any;
    await requestTickets(req1);

    const req2: Request = {} as any;
    await requestTickets(req2);

    expect(req1.tickets).toBeTruthy();
    expect(req2.tickets).toBeTruthy();
    expect(req1.tickets).toBe(req2.tickets);
});
