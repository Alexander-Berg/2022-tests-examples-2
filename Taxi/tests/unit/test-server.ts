import {integer, seed, uuid} from 'casual';
import type http from 'http';
import type net from 'net';
import nock from 'nock';

import {createApp} from 'server/app';
import {config} from 'service/cfg';
import {scanFreePort} from 'service/helper/scan-free-port';
import type {ConfigsResponse} from 'service/realtime-configs';

type NockTvmTicketsInput = {
    dst: 'abc' | 'blackbox' | 'staff';
};

seed(3);

export class TestServer {
    protected url?: string;
    protected server?: http.Server;

    public async getAddress() {
        if (this.url) {
            return this.url;
        }

        const server: http.Server = await createApp({port: await scanFreePort({range: [3100, 3200]}), noHttps: true});

        this.server = server;
        this.url = `http://localhost:${(server.address() as net.AddressInfo).port}`;

        this.nockTvmTickets({dst: 'blackbox'});
        this.nockRealtimeConfigs();

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

    protected nockTvmTickets({dst}: NockTvmTicketsInput) {
        nock(`http://localhost:${config.tvm.port}`)
            .persist()
            .get(`/tvm/tickets?dsts=${config.tvm.destinations[dst]}`)
            .reply(200, {
                [config.tvm.destinations[dst]]: {
                    ticket: uuid,
                    tvm_id: integer()
                }
            });
    }

    protected nockRealtimeConfigs() {
        const response: ConfigsResponse = {
            configs: {
                LAVKA_EAGLE_FEATURES: {}
            },
            updated_at: new Date().toUTCString()
        };
        nock(config.realtimeConfigs.url).persist().post('').reply(200, response);
    }
}
