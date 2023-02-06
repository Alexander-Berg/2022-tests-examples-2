import { AddressInfo } from 'net';
import http, { Server, RequestListener } from 'http';
// import { FirstArgument } from 'shared/types';

import getPort from './get-port';

/**
 * Запускает сервер на свободном порту
 * сервер - это параметр requestListener из `http.createServer` (например инстанс express)
 * @see https://nodejs.org/dist/latest-v10.x/docs/api/http.html#http_http_createserver_options_requestlistener
 *
 * @example
 * const app = express();
 * runServer(app)
 *      .then((server) => {
 *          console.log(`server is running on ${server.address().port} port`);
 *       })
 *
 * @example
 * function yourServerImplementation(req: Request, res: Response) {
 *     res.writeHead(200, { 'Content-Type': 'text/plain' });
 *     res.end('ok');
 * }
 * runServer(yourServerImplementation)
 *      .then((server) => {
 *          console.log(`server is running on ${server.address().port} port`);
 *       })
 */
function runServer(
    cb: RequestListener,
): Promise<{ server: Server; address: AddressInfo }> {
    return new Promise((resolve) => {
        getPort().then((port) => {
            const server = http.createServer(cb).listen(port);

            server.on('listening', () => {
                resolve({ server, address: server.address() as AddressInfo });
            });
        });
    });
}

export { runServer };
