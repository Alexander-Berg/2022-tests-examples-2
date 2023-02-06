import type {ExpressHealthHandler} from '@lavka-js-toolbox/express-health-handler';
import {integer, seed, uuid} from 'casual';
import nock from 'nock';

import {createApp} from '@/src/server/app';
import {config} from 'service/cfg';
import {scanFreePort} from 'service/helper/scan-free-port';

type NockTvmTicketsInput = {
    dst: 'abcDst' | 'blackboxDst' | 'staffDst';
};

seed(3);

export class TestServer {
    protected url?: string;
    protected healthHandler?: ExpressHealthHandler;

    public async getAddress() {
        if (this.url) {
            return this.url;
        }

        const port = await scanFreePort({range: [3100, 3200]});
        const {healthHandler} = await createApp({port, shutdownDelay: 0});

        this.healthHandler = healthHandler;
        this.url = `http://localhost:${port}`;

        this.nockTvmTickets({dst: 'blackboxDst'});

        return this.url;
    }

    public async stop() {
        if (this.healthHandler && !this.healthHandler.isShutdownInProgress()) {
            jest.spyOn(process, 'exit').mockReturnValueOnce(undefined as never);
            await this.healthHandler.shutdown();
        }

        this.healthHandler = undefined;
        this.url = undefined;

        nock.cleanAll();
    }

    protected nockTvmTickets({dst}: NockTvmTicketsInput) {
        nock(`http://localhost:${config.tvm.port}`)
            .persist()
            .get(`/tvm/tickets?dsts=${config.tvm[dst]}`)
            .reply(200, {
                [config.tvm[dst]]: {
                    ticket: uuid,
                    tvm_id: integer()
                }
            });
    }
}
