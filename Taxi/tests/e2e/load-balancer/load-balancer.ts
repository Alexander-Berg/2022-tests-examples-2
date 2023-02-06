import type {Request, Response} from 'express';
import express from 'express';

import assertDefined from '@/src/utils/assert-defined';
import {config} from 'service/cfg';
import {logger} from 'service/logger';

import {routes} from './constants';

const instancesCount = Number(assertDefined(process.env.INSTANCES_COUNT));

const ports = [config.server.port];
while (ports.length < instancesCount) {
    const previousPort = ports[ports.length - 1];
    const nextPort = previousPort + 1;
    ports.push(nextPort);
}

let index = 0;

const balancer = express();

balancer.get(routes.port(), (_req: Request, res: Response) => res.json({port: ports[index++ % ports.length]}));
balancer.get(routes.ports(), (_req: Request, res: Response) => res.json({ports}));

balancer.listen(config.server.balancerPort, () =>
    logger.info(`Load Balancer Server listening on PORT ${config.server.balancerPort}`)
);
