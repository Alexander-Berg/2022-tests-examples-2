// import {integer, uuid} from 'casual';
import type http from 'http';
import type net from 'net';
import nock from 'nock';

import {createApp} from '@/src/server/app';
// import {config} from 'service/cfg';
import {scanFreePort} from 'service/helper/scan-free-port';

// type NockTvmTicketsInput = {
//     dst: 'abcDst' | 'blackboxDst' | 'staffDst';
// };
export class TestServer {
    protected url?: string;
    protected server?: http.Server;

    public async getAddress() {
        if (this.url) {
            return this.url;
        }

        const server: http.Server = await createApp({port: await scanFreePort({range: [3100, 3200]})});

        this.server = server;
        this.url = `http://localhost:${(server.address() as net.AddressInfo).port}`;

        //this.nockTvmTickets({dst: 'blackboxDst'});

        return this.url;
    }

    public async stop() {
        await new Promise<void>((resolve, reject) => {
            if (this.server) {
                this.server.close((error) => (error ? reject(error) : resolve()));
            } else {
                resolve();
            }
        });

        this.server = undefined;

        nock.cleanAll();
    }

    // TODO: образец, как можно мокать работу с tvm
    // protected nockTvmTickets({dst}: NockTvmTicketsInput) {
    //     nock(`http://localhost:${config.tvm.port}`)
    //         .persist()
    //         .get(`/tvm/tickets?dsts=${config.tvm[dst]}`)
    //         .reply(200, {
    //             [config.tvm[dst]]: {
    //                 ticket: uuid,
    //                 tvm_id: integer()
    //             }
    //         });
    // }
}
