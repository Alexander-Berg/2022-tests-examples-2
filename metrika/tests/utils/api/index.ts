import { Request } from 'express';

type Options<T> = T extends (req: Request, opt: infer O) => any ? O : never;

const bindRequest = <T extends (...args: any[]) => any>(apiFunction: T) => {
    const requestImitation: Request = {
        source: 'e2e',
        e2e: {
            oauth: hermione.ctx.user.oauth,
        },
        langdetect: {
            id: 'ru',
        },
    } as any;

    return (options: Options<T>) =>
        apiFunction(requestImitation, options) as ReturnType<T>;
};

export { bindRequest };
