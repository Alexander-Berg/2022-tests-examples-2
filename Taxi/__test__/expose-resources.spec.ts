import {Request} from 'express';

process.env.CFG_DIR = 'node-config';

test('exposeResources cache', async () => {
    const {exposeResources} = await import('../expose-resources');

    const req1: Request = {} as any;
    await exposeResources(req1, {locals: {webpack: {devMiddleware: {stats: {} as any}}}});

    const req2: Request = {} as any;
    await exposeResources(req2, {locals: {webpack: {devMiddleware: {stats: {} as any}}}});

    expect(req1.resources).toBeTruthy();
    expect(req2.resources).toBeTruthy();
    expect(req1.resources).toBe(req2.resources);
});
