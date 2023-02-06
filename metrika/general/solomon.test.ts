import { SolomonMetricsProvider, SolomonSensor, SolomonMetricsData } from './solomon';
import { GaugeMetric, GaugeKind, CounterMetric, HistogramMetric } from '../registry';
import {
    CollectedMetricsDecription,
    getNodeMetricsCollector,
    InternalMetricDescription,
    MetricsSource,
} from '../registry/api';

describe('Solomon backend', () => {
    afterAll(() => {
        getNodeMetricsCollector().stop();
    });

    class MockRegistry implements MetricsSource {
        public metrics: InternalMetricDescription[] = [];
        public getAllMetrics(): CollectedMetricsDecription {
            return {
                tags: {
                    env: 'test',
                },
                metrics: this.metrics,
            };
        }
        // eslint-disable-next-line @typescript-eslint/no-empty-function
        public reset(): void {}
    }

    it('should map given metrics to sensors', () => {
        const registry = new MockRegistry();
        const backend = new SolomonMetricsProvider(registry);
        registry.metrics = [
            {
                name: 'test.gauge.float',
                tags: {
                    kind: 'internal',
                },
                source: new GaugeMetric(GaugeKind.FloatGauge).add(0.1),
            },
            {
                name: 'test.gauge.integer',
                tags: {},
                source: new GaugeMetric(GaugeKind.IntegerGauge).add(10),
            },
            {
                name: 'test.counter',
                tags: {},
                source: new CounterMetric().add(20),
            },
            {
                name: 'test.histogram',
                tags: {},
                source: new HistogramMetric().record(10).record(20).record(30),
            },
        ];
        const expected: SolomonMetricsData = {
            commonLabels: {
                env: 'test',
            },
            sensors: [
                {
                    kind: 'DGAUGE',
                    value: 0.1,
                    labels: {
                        kind: 'internal',
                        name: 'test.gauge.float',
                    },
                },
                {
                    kind: 'IGAUGE',
                    value: 10,
                    labels: {
                        name: 'test.gauge.integer',
                    },
                },
                {
                    kind: 'COUNTER',
                    value: 20,
                    labels: {
                        name: 'test.counter',
                    },
                },
                {
                    kind: 'DGAUGE',
                    value: 20,
                    labels: {
                        name: 'test.histogram.mean',
                    },
                },
                {
                    kind: 'DGAUGE',
                    value: 10,
                    labels: {
                        name: 'test.histogram.stddev',
                    },
                },
                {
                    type: 'HIST',
                    labels: {
                        name: 'test.histogram.hist',
                    },
                    hist: {
                        bounds: new Array(15).fill(0).map((v, i) => Math.pow(2, i) * 0.001),
                        buckets: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                        inf: 2,
                    },
                },
            ],
        };
        const actual = backend.getMetrics();
        expect(sortedSensors(actual.sensors)).toEqual(sortedSensors(expected.sensors));
    });
});

function sortedSensors(sensors: SolomonSensor[]): SolomonSensor[] {
    return [...sensors].sort((a, b) => (a.labels.name > b.labels.name ? 1 : -1));
}
