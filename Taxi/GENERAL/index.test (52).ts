import nock from 'nock';

import {createSensor, MetricProvider, Pusher, Signal, SOLOMON_AGENT_URL, solomonPusher} from '.';

describe('package "metric"', () => {
    beforeAll(async () => {
        nock.disableNetConnect();
        nock.enableNetConnect(/localhost/);
    });

    afterAll(async () => {
        nock.enableNetConnect();
    });

    afterEach(async () => {
        nock.cleanAll();
    });

    it('should create sensor and signal', () => {
        const sampleSensor = createSensor<{foo: string}>({
            sensor: 'sample',
            commonLabels: {
                application: 'jstoolbox',
                env: 'test'
            }
        });

        expect(sampleSensor({foo: 'bar'})).toEqual({
            commonLabels: {application: 'jstoolbox', env: 'test'},
            sensors: [{labels: {foo: 'bar', sensor: 'sample'}, ts: expect.any(Number), value: 1}]
        });

        expect(sampleSensor(50, {foo: 'baz'})).toEqual({
            commonLabels: {application: 'jstoolbox', env: 'test'},
            sensors: [{labels: {foo: 'baz', sensor: 'sample'}, ts: expect.any(Number), value: 50}]
        });
    });

    it('should push signal', async () => {
        const sampleSensor = createSensor({sensor: 'sample'});
        const {signals, pusher} = createArrayPusher();
        const provider = new MetricProvider({pusher});

        await provider.push(sampleSensor());
        await provider.push(sampleSensor(25));

        expect(signals).toEqual([
            {sensors: [{labels: {sensor: 'sample'}, ts: expect.any(Number), value: 1}]},
            {sensors: [{labels: {sensor: 'sample'}, ts: expect.any(Number), value: 25}]}
        ]);
    });

    it('should push many signals to many pushers', async () => {
        const sensorA = createSensor({sensor: 'sensorA'});
        const sensorB = createSensor({sensor: 'sensorB'});

        const {signals: signalsA, pusher: pusherA} = createArrayPusher();
        const {signals: signalsB, pusher: pusherB} = createArrayPusher();

        const provider = new MetricProvider({pusher: [pusherA, pusherB]});

        await provider.push(sensorA(), sensorB(5));

        expect(signalsA).toEqual(signalsB);
        expect(signalsA).toEqual([
            {sensors: [{labels: {sensor: 'sensorA'}, ts: expect.any(Number), value: 1}]},
            {sensors: [{labels: {sensor: 'sensorB'}, ts: expect.any(Number), value: 5}]}
        ]);
    });

    it('should handle Solomon pusher', async () => {
        const sampleSensor = createSensor({sensor: 'sample'});
        const pusher = solomonPusher({solomonAgentUrl: SOLOMON_AGENT_URL});
        const provider = new MetricProvider({pusher});

        let parsedBody = null;

        const scope = nock(SOLOMON_AGENT_URL)
            .post('/', (body) => {
                parsedBody = body;
                return body;
            })
            .reply(200, {ok: true});

        await provider.push(sampleSensor());

        expect(parsedBody).toEqual({sensors: [{labels: {sensor: 'sample'}, ts: expect.any(Number), value: 1}]});
        expect(scope.isDone()).toBe(true);
    });
});

function createArrayPusher() {
    const signals: Signal[] = [];
    const pusher: Pusher = async (signal) => {
        signals.push(signal);
    };
    return {signals, pusher};
}
