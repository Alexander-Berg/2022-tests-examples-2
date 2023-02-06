import net, { AddressInfo } from 'net';

/**
 * ищет свободный порт в системе
 * @example
 * getPort().then((port) => {
 *      console.log(port); // 12345
 * })
 */
export default function getPort() {
    return new Promise((resolve) => {
        const server = net.createServer();

        server.listen(0, () => {
            const port = (server.address() as AddressInfo).port;
            server.close(() => {
                resolve(port);
            });
        });
    });
}
