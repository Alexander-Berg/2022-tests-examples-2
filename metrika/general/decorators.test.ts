import { CounterMetric, GaugeMetric } from '../registry';
import { Metrics, InvokeCounter, InvokeInProgressCount, ErrorCounter } from './decorators';
import { CancelablePromise, SmartPromise } from '../../node-tools/smart-promise';
import { getMetricsSource, getNodeMetricsCollector } from '../registry/api';

describe('Metrics decorators', () => {
    const metrics = getMetricsSource();
    beforeEach(() => {
        metrics.reset();
    });
    beforeAll(() => {
        process.env.ENV = 'TESTING';
    });
    afterAll(() => {
        getNodeMetricsCollector().stop();
    });

    describe('InvokeCounter', () => {
        it('should increase counter when function is called', () => {
            @Metrics('test')
            class TestClass {
                @InvokeCounter('call.count')
                public call(): undefined {
                    return undefined;
                }
            }

            const obj = new TestClass();
            expect(obj.call()).toBeUndefined();
            const countMetric = metrics.getAllMetrics().metrics[0];
            const metricSource = countMetric.source as CounterMetric;

            expect(countMetric.name).toEqual('test.call.count');
            expect(metricSource instanceof CounterMetric).toBeTruthy();
            expect(metricSource.getValue()).toEqual(1);
            expect(countMetric.tags).toEqual({});
        });
    });

    describe('InvokeInProgressCount', () => {
        describe('when result is a promise', () => {
            it('should increase gauge when function is called', () => {
                @Metrics('test')
                class TestClass {
                    @InvokeInProgressCount('call.active.count')
                    public async call(): Promise<void> {
                        return new Promise<void>(res => {
                            this.resolve = res;
                        });
                    }
                    // eslint-disable-next-line @typescript-eslint/no-empty-function
                    public resolve(): void {}
                }
                const obj = new TestClass();
                void obj.call();
                const countMetric = metrics.getAllMetrics().metrics[0];
                const metricSource = countMetric.source as GaugeMetric;
                obj.resolve();

                expect(countMetric.name).toEqual('test.call.active.count');
                expect(metricSource instanceof GaugeMetric).toBeTruthy();
                expect(metricSource.getValue()).toEqual(1);
                expect(countMetric.tags).toEqual({});
            });

            it('should decrease gauge when function call has ended', async () => {
                @Metrics('test')
                class TestClass {
                    @InvokeInProgressCount('call.active.count')
                    public async call(): Promise<void> {
                        return new Promise<void>(res => {
                            this.resolve = res;
                        });
                    }
                    // eslint-disable-next-line @typescript-eslint/no-empty-function
                    public resolve(): void {}
                }

                const obj = new TestClass();
                const result = obj.call();
                obj.resolve();
                await result;
                const countMetric = metrics.getAllMetrics().metrics[0];
                const metricSource = countMetric.source as GaugeMetric;

                expect(countMetric.name).toEqual('test.call.active.count');
                expect(metricSource instanceof GaugeMetric).toBeTruthy();
                expect(metricSource.getValue()).toEqual(0);
                expect(countMetric.tags).toEqual({});
            });

            it('should decrease gauge when function ended with error', async () => {
                @Metrics('test')
                class TestClass {
                    @InvokeInProgressCount('call.active.count')
                    public async call(): Promise<void> {
                        return new Promise<void>((_, reject) => {
                            this.reject = (): void => reject(new Error('Test error'));
                        });
                    }
                    // eslint-disable-next-line @typescript-eslint/no-empty-function
                    public reject = (): void => {};
                }

                const obj = new TestClass();
                const result = obj.call();
                obj.reject();
                await expect(result).rejects.toThrowError();
                const countMetric = metrics.getAllMetrics().metrics[0];
                const metricSource = countMetric.source as GaugeMetric;

                expect(countMetric.name).toEqual('test.call.active.count');
                expect(metricSource instanceof GaugeMetric).toBeTruthy();
                expect(metricSource.getValue()).toEqual(0);
                expect(countMetric.tags).toEqual({});
            });
        });

        describe('when result is a SmartPromise', () => {
            it('should increase gauge when function is called', async () => {
                @Metrics('test')
                class TestClass {
                    public promise = new SmartPromise<void>();

                    @InvokeInProgressCount('call.active.count')
                    public call(): CancelablePromise<void> {
                        return this.promise;
                    }
                }

                const obj = new TestClass();
                obj.call();
                const countMetric = metrics.getAllMetrics().metrics[0];
                const metricSource = countMetric.source as GaugeMetric;
                obj.promise.resolve();

                expect(countMetric.name).toEqual('test.call.active.count');
                expect(metricSource instanceof GaugeMetric).toBeTruthy();
                expect(metricSource.getValue()).toEqual(1);
                expect(countMetric.tags).toEqual({});
            });

            it('should decrease gauge when function call has ended', async () => {
                @Metrics({ prefix: 'test' })
                class TestClass {
                    public promise = new SmartPromise<void>();

                    @InvokeInProgressCount('call.active.count')
                    public call(): CancelablePromise<void> {
                        return this.promise;
                    }
                }

                const obj = new TestClass();
                const result = obj.call();
                obj.promise.resolve();
                await result.promise;
                const countMetric = metrics.getAllMetrics().metrics[0];
                const metricSource = countMetric.source as GaugeMetric;

                expect(countMetric.name).toEqual('test.call.active.count');
                expect(metricSource instanceof GaugeMetric).toBeTruthy();
                expect(metricSource.getValue()).toEqual(0);
                expect(countMetric.tags).toEqual({});
            });

            it('should decrease gauge when function call ended with error', async () => {
                @Metrics({ prefix: 'test' })
                class TestClass {
                    public promise = new SmartPromise<void>();

                    @InvokeInProgressCount('call.active.count')
                    public call(): CancelablePromise<void> {
                        return this.promise;
                    }
                }

                const obj = new TestClass();
                const result = obj.call();
                obj.promise.reject(new Error('Test error'));
                await expect(result.promise).rejects.toThrowError();
                const countMetric = metrics.getAllMetrics().metrics[0];
                const metricSource = countMetric.source as GaugeMetric;

                expect(countMetric.name).toEqual('test.call.active.count');
                expect(metricSource instanceof GaugeMetric).toBeTruthy();
                expect(metricSource.getValue()).toEqual(0);
                expect(countMetric.tags).toEqual({});
            });
        });
    });

    describe('ErrorCounter', () => {
        it('should register error when result is a promise', async () => {
            @Metrics('test')
            class TestClass {
                @ErrorCounter('call.errors')
                public call(): Promise<void> {
                    return new Promise<void>((_, reject) => {
                        this.reject = (): void => reject(new Error('Test error'));
                    });
                }
                // eslint-disable-next-line @typescript-eslint/no-empty-function
                public reject(): void {}
            }

            const obj = new TestClass();
            const result = obj.call();
            obj.reject();
            await expect(result).rejects.toThrowError();
            const countMetric = metrics.getAllMetrics().metrics[0];
            const metricSource = countMetric.source as CounterMetric;

            expect(countMetric.name).toEqual('test.call.errors');
            expect(metricSource instanceof CounterMetric).toBeTruthy();
            expect(metricSource.getValue()).toEqual(1);
            expect(countMetric.tags).toEqual({ errorName: 'Error' });
        });

        it('should register error when result is a SmartPromise', async () => {
            @Metrics('test')
            class TestClass {
                public promise = new SmartPromise<void>();

                @ErrorCounter('call.errors')
                public call(): CancelablePromise<void> {
                    return this.promise;
                }
            }

            const obj = new TestClass();
            const result = obj.call();
            obj.promise.reject(new Error('Test error'));
            await expect(result.promise).rejects.toThrowError();
            const countMetric = metrics.getAllMetrics().metrics[0];
            const metricSource = countMetric.source as CounterMetric;

            expect(countMetric.name).toEqual('test.call.errors');
            expect(metricSource instanceof CounterMetric).toBeTruthy();
            expect(metricSource.getValue()).toEqual(1);
            expect(countMetric.tags).toEqual({ errorName: 'Error' });
        });

        it('should not register error when result is a canceled SmartPromise', async () => {
            @Metrics('test')
            class TestClass {
                public promise = new SmartPromise<void>();

                @ErrorCounter('call.errors')
                public call(): CancelablePromise<void> {
                    return this.promise;
                }
            }

            const obj = new TestClass();
            const result = obj.call();
            await obj.promise.cancel();
            await expect(result.promise).rejects.toThrowError();
            const countMetric = metrics.getAllMetrics().metrics;

            expect(countMetric.length).toEqual(0);
        });

        it('should register error when result is not a promise', async () => {
            @Metrics('test')
            class TestClass {
                @ErrorCounter('call.errors')
                public call(): void {
                    throw new Error('Test error');
                }
            }

            const obj = new TestClass();
            expect(() => obj.call()).toThrowError();
            const countMetric = metrics.getAllMetrics().metrics[0];
            const metricSource = countMetric.source as CounterMetric;

            expect(countMetric.name).toEqual('test.call.errors');
            expect(metricSource instanceof CounterMetric).toBeTruthy();
            expect(metricSource.getValue()).toEqual(1);
            expect(countMetric.tags).toEqual({ errorName: 'Error' });
        });
    });
});
