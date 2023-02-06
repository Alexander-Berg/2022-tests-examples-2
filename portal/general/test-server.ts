/* eslint no-console: 0 */

require('../../../alias');
import * as http from 'http';
import {Response} from 'express';
import {RequestListener, IncomingMessage} from 'http';
import {parse as urlParse} from 'url';
import {experiments, RequestWithExps} from '@server/libs/experiments';
import * as apiSearchV2 from './api_search_2.json';
import {cards} from './blocks/div2/app';
import {mockResponse} from './tests/mock-response';
import {req as mockReq} from './tests/mocks';
import {I18n} from './i18n';
import {getAppDivOpts} from './blocks/app-div-options';
import {getLogger} from 'portal-node-logger';
import {Div2Card} from './blocks/app-card';

const fqdn = require('fqdn-resolver');

const PORTS = {min: 9876, max: 9885};
const logger = getLogger({write_to_console: true}, 'tests');
mockReq.logger = logger;
experiments.init(mockReq as unknown as RequestWithExps, null as unknown as Response, () => undefined);

async function mockApiSearch2Response({
    cardId,
    isLegacy,
    isDark,
    state
}: {
    cardId: string,
    isLegacy: boolean,
    isDark: boolean,
    state: string
}): Promise<object> {
    const card = cards.find(card => card.config.id === cardId);
    const req: any = Object.assign({}, mockReq);
    if (!card) {
        throw new Error(`No card with id=${cardId}`);
    }

    if (!isLegacy) {
        req.flags = {redesign_div_pp: 1};
    }

    if (isDark) {
        req._useDarkColors = true;
    }

    const mockName = state ? `${cardId}_${state}` : cardId;
    const opts = getAppDivOpts(req.post_data[cardId], req, req.data[cardId]);

    const mock = await mockResponse(mockName, card.fetch.bind(null), opts);
    const block = card.render(new I18n('ru'), opts, mock);
    const cardTemplates = (block as Div2Card).templates;

    const res = {...apiSearchV2} as any;

    res.block = [block];
    res.layout = [{type: block.type, heavy: 0, id: cardId}];
    res.div_templates = cardTemplates;
    return res;
}

const requestListener: RequestListener = (req: IncomingMessage, res: http.ServerResponse) => {
    if (!req.url) {
        throw new Error('no url');
    }

    const url = urlParse(req.url, true);
    const cardId = url.query.cardId as string;
    const state = url.query.state as string;
    const isLegacy = url.query.legacy === 'true';
    const isDark = url.query.isDark === 'true';

    res.writeHead(200, {'Content-Type': 'text/json'});
    mockApiSearch2Response({cardId, isLegacy, isDark, state}).then(response => res.end(JSON.stringify(response))).catch(err => {
        console.error(err);
        res.writeHead(500);
        res.end('');
    });
};

export async function run(): Promise<{
    port: number,
    ip: string,
    hostname: string,
    server: http.Server
}> {
    const {hostname, ip} = await fqdn();

    return new Promise((resolve, reject) => {
        const server = http.createServer(requestListener);
        let port = PORTS.min;

        server.on('error', err => {
            if ((err as any).code === 'EADDRINUSE') {
                console.error('EADDRINUSE', port);

                port += 1;

                if (port > PORTS.max) {
                    console.error('All ports are taken');
                    process.exit(1);
                } else {
                    server.listen(port);
                }
            } else {
                reject(err);
            }
        });

        server.listen(port, function () {
            resolve({server, hostname, ip, port});
        });
    });
}

if (require.main === module) {
    run()
        .then(({hostname, port}) => {
            console.log(`listening on http://${hostname}:${port}`);
            return;
        })
        .catch(e => {
            console.error(e);
        });
}
