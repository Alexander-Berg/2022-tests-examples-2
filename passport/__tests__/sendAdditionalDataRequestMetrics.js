import sendMetrics from '../sendAdditionalDataRequestMetrics';
import {ADDITIONAL_DATA_REQUEST_METRICS_PREFIX} from '../../metrics_constants';
import metrics from '../../../metrics';

jest.mock('../../../metrics', () => ({
    send: jest.fn(),
    goal: jest.fn()
}));

describe('Action: sendAdditionalDataRequestMetrics', () => {
    afterEach(() => {
        metrics.send.mockClear();
        metrics.goal.mockClear();
    });

    it('should send metrics with some type', () => {
        const getState = jest.fn(() => ({
            additionalDataRequest: {}
        }));
        const type = 'some_type';
        const head = 'head';
        const act = 'act';

        sendMetrics(type, head, act)(null, getState);

        expect(metrics.send).toBeCalled();
        expect(metrics.goal).toBeCalled();
        expect(metrics.goal).toBeCalledWith(`${ADDITIONAL_DATA_REQUEST_METRICS_PREFIX}_${type}`);
    });

    it('should send metrics with some_type and any action', () => {
        const getState = jest.fn(() => ({
            additionalDataRequest: {
                action: 'any'
            }
        }));
        const type = 'some_type';
        const head = 'head';
        const act = 'act';

        sendMetrics(type, head, act)(null, getState);

        expect(metrics.send).toBeCalled();
        expect(metrics.goal).toBeCalled();
        expect(metrics.goal).toBeCalledWith(`${ADDITIONAL_DATA_REQUEST_METRICS_PREFIX}_${type}`);
    });

    it('should send metrics with skip_phone type', () => {
        const getState = jest.fn(() => ({
            additionalDataRequest: {
                action: 'add'
            }
        }));
        const type = 'skip_phone';
        const head = 'head';
        const act = 'act';

        sendMetrics(type, head, act)(null, getState);

        expect(metrics.send).toBeCalled();
        expect(metrics.goal).toBeCalled();
        expect(metrics.goal).toBeCalledWith(`${ADDITIONAL_DATA_REQUEST_METRICS_PREFIX}_${type}`);
    });

    it('should send metrics with show_phone type', () => {
        const getState = jest.fn(() => ({
            additionalDataRequest: {
                action: 'secure'
            }
        }));
        const type = 'show_phone';
        const head = 'head';
        const act = 'act';

        sendMetrics(type, head, act)(null, getState);

        expect(metrics.send).toBeCalled();
        expect(metrics.goal).toBeCalled();
        expect(metrics.goal).toBeCalledWith(`${ADDITIONAL_DATA_REQUEST_METRICS_PREFIX}_${type}`);
    });

    it('should send metrics with admit action', () => {
        const getState = jest.fn(() => ({
            additionalDataRequest: {
                action: 'admit'
            }
        }));
        const type = 'show_phone';
        const head = 'head';
        const act = 'act';

        sendMetrics(type, head, act)(null, getState);

        expect(metrics.send).toBeCalled();
        expect(metrics.goal).toBeCalled();
        expect(metrics.goal).toBeCalledWith(`${ADDITIONAL_DATA_REQUEST_METRICS_PREFIX}_${type}`);
    });

    it('should send metrics with any action', () => {
        const getState = jest.fn(() => ({
            additionalDataRequest: {
                action: 'any'
            }
        }));
        const type = 'show_phone';
        const head = 'head';
        const act = 'act';

        sendMetrics(type, head, act)(null, getState);

        expect(metrics.send).toBeCalled();
        expect(metrics.goal).toBeCalled();
        expect(metrics.goal).toBeCalledWith(`${ADDITIONAL_DATA_REQUEST_METRICS_PREFIX}_${type}`);
    });

    it('should send metrics with skip_email type', () => {
        const getState = jest.fn(() => ({
            additionalDataRequest: {
                action: 'add'
            }
        }));
        const type = 'skip_email';
        const head = null;
        const act = 'act';

        sendMetrics(type, head, act)(null, getState);

        expect(metrics.send).toBeCalled();
        expect(metrics.goal).toBeCalled();
        expect(metrics.goal).toBeCalledWith(`${ADDITIONAL_DATA_REQUEST_METRICS_PREFIX}_${type}`);
    });

    it('should send metrics with show_email type', () => {
        const getState = jest.fn(() => ({
            additionalDataRequest: {
                action: 'restore'
            }
        }));
        const type = 'show_email';
        const head = null;
        const act = 'act';

        sendMetrics(type, head, act)(null, getState);

        expect(metrics.send).toBeCalled();
        expect(metrics.goal).toBeCalled();
        expect(metrics.goal).toBeCalledWith(`${ADDITIONAL_DATA_REQUEST_METRICS_PREFIX}_${type}`);
    });

    it('should send metrics with any action', () => {
        const getState = jest.fn(() => ({
            additionalDataRequest: {
                action: 'confirm'
            }
        }));
        const type = 'show_email';
        const head = null;
        const act = 'act';

        sendMetrics(type, head, act)(null, getState);

        expect(metrics.send).toBeCalled();
        expect(metrics.goal).toBeCalled();
        expect(metrics.goal).toBeCalledWith(`${ADDITIONAL_DATA_REQUEST_METRICS_PREFIX}_${type}`);
    });

    it('should send metrics with skip_social type', () => {
        const getState = jest.fn(() => ({
            additionalDataRequest: {
                action: 'add'
            }
        }));
        const type = 'skip_social';
        const head = null;
        const act = 'act';

        sendMetrics(type, head, act)(null, getState);

        expect(metrics.send).toBeCalled();
        expect(metrics.goal).toBeCalled();
        expect(metrics.goal).toBeCalledWith(`${ADDITIONAL_DATA_REQUEST_METRICS_PREFIX}_${type}`);
    });

    it('should send metrics with show_social type', () => {
        const getState = jest.fn(() => ({
            additionalDataRequest: {
                action: 'allow_auth'
            }
        }));
        const type = 'show_social';
        const head = null;
        const act = 'act';

        sendMetrics(type, head, act)(null, getState);

        expect(metrics.send).toBeCalled();
        expect(metrics.goal).toBeCalled();
        expect(metrics.goal).toBeCalledWith(`${ADDITIONAL_DATA_REQUEST_METRICS_PREFIX}_${type}`);
    });

    it('should send metrics with any action', () => {
        const getState = jest.fn(() => ({
            additionalDataRequest: {
                action: 'any'
            }
        }));
        const type = 'show_social';
        const head = null;
        const act = 'act';

        sendMetrics(type, head, act)(null, getState);

        expect(metrics.send).toBeCalled();
        expect(metrics.goal).toBeCalled();
        expect(metrics.goal).toBeCalledWith(`${ADDITIONAL_DATA_REQUEST_METRICS_PREFIX}_${type}`);
    });
});
