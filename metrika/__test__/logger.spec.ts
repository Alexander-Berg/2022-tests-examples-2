import * as chai from 'chai';
import * as sinon from 'sinon';
import * as counter from '@src/utils/counter';
import { METHOD_NAME_HIT } from '@src/providers/artificialHit/type';
import {
    METHOD_NAME_ADD_FILE_EXTENSION,
    METHOD_NAME_EXTERNAL_LINK_CLICK,
    METHOD_NAME_FILE_CLICK,
    METHOD_NAME_TRACK_LINKS,
} from '@src/providers/clicks/const';
import { METHOD_DESTRUCT } from '@src/providers/destruct/const';
import { METHOD_NAME_EXPERIMENTS } from '@src/providers/experiments/const';
import { METHOD_NAME_GET_CLIENT_ID } from '@src/providers/getClientID/const';
import { METHOD_NAME_GOAL } from '@src/providers/goal/const';
import { METHOD_NAME_NOT_BOUNCE } from '@src/providers/notBounce/const';
import { METHOD_NAME_PARAMS } from '@src/providers/params/const';
import { METHOD_NAME_SET_USER_ID } from '@src/providers/setUserID/const';
import { METHOD_NAME_USER_PARAMS } from '@src/providers/userParams/const';
import { CounterObject } from '@src/utils/counter/type';
import { LoggerData } from '../const';
import * as loggerLib from '../logger';

describe('phoneChanger / logger', () => {
    const sandbox = sinon.createSandbox();
    let logger: LoggerData;
    const cliId = '1';
    const orderId = '2';
    const serviceId = '3';
    const clientIdAlt = '2';
    beforeEach(() => {
        logger = loggerLib.useLogger(window, {
            id: 123456,
            counterType: '0',
        });
    });
    afterEach(() => {
        sandbox.restore();
    });

    it('Collect records while not Ready', () => {
        loggerLib.loggerLog(
            logger,
            { cliId, orderId, serviceId },
            [['123', '345']],
            [['1123', '1345']],
            5,
        );
        loggerLib.loggerLog(
            logger,
            { cliId, orderId, serviceId },
            [['123', '345']],
            [['1123', '1345']],
            5,
        );
        loggerLib.loggerLog(
            logger,
            { cliId, orderId, serviceId },
            [['123', '345']],
            [['1123', '1345']],
            5,
        );

        chai.expect(logger.cliId).to.equal(cliId);
        chai.expect(logger.orderId).to.equal(orderId);
        chai.expect(logger.serviceId).to.equal(serviceId);
        chai.expect(logger.phones).to.deep.equal({
            '123': {
                '345': 3,
            },
            '1123': {
                '1345': 0,
            },
        });
        chai.expect(logger.perf).to.deep.equal([5, 5, 5]);
    });
    it('Reset on change clientId', () => {
        loggerLib.loggerLog(
            logger,
            { cliId, orderId, serviceId },
            [['123', '345']],
            [['1123', '1345']],
            5,
        );
        loggerLib.loggerLog(
            logger,
            { cliId, orderId, serviceId },
            [['123', '345']],
            [['1123', '1345']],
            5,
        );
        loggerLib.loggerLog(
            logger,
            { cliId: clientIdAlt, orderId, serviceId },
            [['123', '345']],
            [['1123', '1345']],
            5,
        );

        chai.expect(logger.cliId).to.equal(clientIdAlt);
        chai.expect(logger.orderId).to.equal(orderId);
        chai.expect(logger.serviceId).to.equal(serviceId);
        chai.expect(logger.phones).to.deep.equal({
            '123': { '345': 1 },
            '1123': { '1345': 0 },
        });
        chai.expect(logger.perf.length).to.equal(3);
    });
    it('Change onReady', () => {
        chai.expect(logger.isReady).to.equal(false);
        loggerLib.loggerSetReady(logger);
        chai.expect(logger.isReady).to.equal(true);
    });
    it('call log in Ready state', () => {
        const getCounterInstanceStub = sandbox.stub(
            counter,
            'getCounterInstance',
        );
        let counterObject: CounterObject = {} as CounterObject;
        const func = () => counterObject;
        counterObject = {
            [METHOD_NAME_HIT]: func,
            [METHOD_NAME_PARAMS]: (...params) => {
                chai.expect(params[0]).to.equal('__ym');
                chai.expect(params[1]).to.equal('phc');
                const data = params[2];
                chai.expect(data.phones).to.deep.equal({
                    '123': {
                        '345': 3,
                    },
                    '1123': {
                        '1345': 0,
                    },
                });
                chai.expect(data.performance).to.deep.equal([5, 5, 5]);
                return counterObject;
            },
            [METHOD_NAME_EXPERIMENTS]: func,
            [METHOD_NAME_GOAL]: func,
            [METHOD_NAME_USER_PARAMS]: func,
            [METHOD_NAME_NOT_BOUNCE]: func,
            [METHOD_NAME_ADD_FILE_EXTENSION]: func,
            [METHOD_NAME_EXTERNAL_LINK_CLICK]: func,
            [METHOD_NAME_FILE_CLICK]: func,
            [METHOD_NAME_TRACK_LINKS]: func,
            [METHOD_NAME_SET_USER_ID]: func,
            [METHOD_NAME_GET_CLIENT_ID]: () => '',
            [METHOD_DESTRUCT]: func,
        };
        getCounterInstanceStub.callsFake(() => counterObject);

        loggerLib.loggerLog(
            logger,
            { cliId, orderId, serviceId },
            [['123', '345']],
            [['1123', '1345']],
            5,
        );
        loggerLib.loggerLog(
            logger,
            { cliId, orderId, serviceId },
            [['123', '345']],
            [['1123', '1345']],
            5,
        );
        loggerLib.loggerSetReady(logger);
        loggerLib.loggerLog(
            logger,
            { cliId, orderId, serviceId },
            [['123', '345']],
            [['1123', '1345']],
            5,
        );
    });
});
