import { NextFunction, Request, Response } from 'express';
import got from 'got';
import { noop, castArray } from 'lodash';

interface SimpleRequest {
    endpoint?: string;
    path: string;
}

interface SimpleRequestsMiddlewareOptions {
    endpoint: string;
    urls: Array<SimpleRequest | SimpleRequest[]>;
}

/**
 * Мидлвара, которая делает запросы
 *
 * @example
 * const app = express();
 * app.use(
 *      requestsMiddleware({
 *          endpoint: 'http://localhost:12345',
 *          urls: [
 *              { path: '/path/1' },
 *              [{ path: '/path/2' }, { endpoint: 'http://example.com', path: '/path/3' }],
 *              { path: '/path/4' },
 *          ],
 *      })
 * );
 *
 * app.get('/test', (req, res) => {
 *      res.status(200).send('ok');
 * });
 *
 * При запросе /test сервер сходит сначала на localhost:12345/path/1
 * затем сделает два параллельных запроса на localhost:12345/path/2 и example.com/path/3
 * потом на localhost:12345/path/4
 * потом отдаст ответ 'ok'
 */
function requestsMiddleware({
    urls,
    endpoint,
}: SimpleRequestsMiddlewareOptions) {
    return async (req: Request, res: Response, next: NextFunction) => {
        for (const url of urls) {
            const promises = castArray(url).map((url) =>
                got(`${url.endpoint ?? endpoint}${url.path}`, {
                    retry: 0,
                }).then(noop, noop),
            );

            await Promise.all(promises);
        }

        next();
    };
}

export { requestsMiddleware };
