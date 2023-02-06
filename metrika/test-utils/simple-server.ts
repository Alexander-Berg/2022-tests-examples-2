import { RequestListener } from 'http';
import express from 'express';

/**
 * @description Возвращает простой express сервер
 * @example
 * import { getSimpleServer } from 'simple-server';
 * import { runServer } from 'run-server';
 *
 * runServer(getSimpleServer()).then((server) => {
 *      const endpoint = `http://localhost:${server.address().port}`;
 *
 *      request(`${endpoint}/success/any/string`).then(...); // 200 { status: 'OK' }
 *      request(`${endpoint}/error/any/string`).then(...); // 500 { status: 'FAIL' }
 *      request(`${endpoint}/redirect/success/any/string`); // 302 -> 200 { status: 'OK' }
 *      request(`${endpoint}/redirect/error/any/string`); // 302 -> 500 { status: 'FAIL' }
 *
 *      // Можно передавать таймауты на ответ/редирект
 *      request(`${endpoint}/success/any/string?timeout=1000`); // ответит минимум через 1 сек
 * });
 *
 * после окончания тестов нужно закрыть сервер, чтобы освободить порт
 * пример в afterAll
 * @example
 * afterAll(() => {
 *      return new Promise((resolve) => server.close(resolve));
 * });
 *
 * В jest есть замечательные моки, которых хватает в 99.9% случаев
 * используйте этот модуль только в случае действительной необходимости
 */
function getServer() {
    const app = express();

    app.use((req, res, next) => {
        // @ts-ignore
        req.timeout = Number(req.query.timeout) || 50;
        next();
    });

    app.all(/^\/success\/?/, (req, res) => {
        setTimeout(() => {
            res.status(200).json({ status: 'OK' });
        }, (req as any).timeout);
    });

    app.all(/^\/error\/?/, (req, res) => {
        setTimeout(() => {
            res.status(500).json({ status: 'FAIL' });
        }, (req as any).timeout);
    });

    app.all('/redirect/:to', (req, res) => {
        setTimeout(() => {
            res.redirect(`/${req.params.to}`);
        }, (req as any).timeout);
    });

    return (app as any) as RequestListener;
}

export { getServer };
