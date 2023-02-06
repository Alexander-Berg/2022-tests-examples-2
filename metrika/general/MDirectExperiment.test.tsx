// import * as React from 'react';
import {
    MDirectExperiment,
    EXPERIMENT_MAX_SEGMENTS,
    EXPERIMENT_MIN_SEGMENTS,
} from './MDirectExperiment';
import { clone } from 'mobx-state-tree';

function experimentGenerator({
    name,
    generateIds = false,
    ratios,
}: {
    name: string;
    generateIds?: boolean;
    ratios: number[];
}) {
    return MDirectExperiment.create({
        name,
        id: generateIds ? 1 : null,
        active: true,
        counters: [{ id: 1, name: 'счётчик' }],
        segments: ratios.map((ratio, idx) => ({
            ratio,
            id: generateIds ? idx : null,
            name: `segment #${idx}`,
        })),
    });
}

describe('MDirectExperiment', () => {
    describe('views', () => {
        describe('canEditCounter - ', () => {
            it('on new experiment', () => {
                const experiment = experimentGenerator({
                    name: 'qwerty',
                    // tslint:disable-next-line
                    ratios: new Array(EXPERIMENT_MIN_SEGMENTS).fill(10),
                });

                expect(
                    experiment.canEditCounter(experiment.counters[0]),
                ).toBeTruthy();
            });

            it('on saved experiment', () => {
                const experiment = experimentGenerator({
                    name: 'qwerty',
                    generateIds: true,
                    // tslint:disable-next-line
                    ratios: new Array(EXPERIMENT_MIN_SEGMENTS).fill(10),
                });

                expect(
                    experiment.canEditCounter(experiment.counters[0]),
                ).toBeFalsy();
            });

            it('on saved experiment after add new counter', () => {
                const experiment = experimentGenerator({
                    name: 'qwerty',
                    generateIds: true,
                    // tslint:disable-next-line
                    ratios: new Array(EXPERIMENT_MIN_SEGMENTS).fill(10),
                });
                experiment.addCounter({
                    id: 2,
                    name: 'qweqwe',
                    status: 'Active',
                    isRestricted: false,
                });

                expect(
                    experiment.canEditCounter(experiment.counters[1]),
                ).toBeTruthy();
            });
        });
        describe('canDeleteSegment - ', () => {
            it('new experiment with minimal amount of segments', () => {
                const experiment1 = experimentGenerator({
                    name:
                        'Новый эксперимент с минимальным количеством сегментов',
                    // tslint:disable-next-line
                    ratios: new Array(EXPERIMENT_MIN_SEGMENTS).fill(10),
                });
                const canDeleteAnySegment1 = experiment1.segments.some((s) =>
                    experiment1.canDeleteSegment(s),
                );
                expect(canDeleteAnySegment1).toBe(false);

                const canDeleteAnyUsualSegment1 = experiment1.segments
                    .filter((s) => s !== experiment1.lastSegment)
                    .some((s) => experiment1.canDeleteSegment(s));

                expect(canDeleteAnyUsualSegment1).toBe(false);
            });
            it('new experiment with not minimal amount of segments', () => {
                const experiment1 = experimentGenerator({
                    name:
                        'Новый эксперимент с не минимальным количеством сегментов',
                    // tslint:disable-next-line
                    ratios: new Array(EXPERIMENT_MIN_SEGMENTS + 2).fill(10),
                });
                const canDeleteAnySegment1 = experiment1.segments.some((s) =>
                    experiment1.canDeleteSegment(s),
                );
                expect(canDeleteAnySegment1).toBe(true);

                const canDeleteEveryUsualSegment1 = experiment1.segments
                    .filter((s) => s !== experiment1.lastSegment)
                    .every((s) => experiment1.canDeleteSegment(s));

                expect(canDeleteEveryUsualSegment1).toBe(true);

                expect(
                    experiment1.canDeleteSegment(experiment1.lastSegment),
                ).toBe(false);
            });
            it('saved experiment', () => {
                const experiment1 = experimentGenerator({
                    name:
                        'Сохранённый эксперимент с минимальным количеством сегментов',
                    generateIds: true,
                    // tslint:disable-next-line
                    ratios: new Array(EXPERIMENT_MIN_SEGMENTS).fill(10),
                });
                const canDeleteAnySegment1 = experiment1.segments.some((s) =>
                    experiment1.canDeleteSegment(s),
                );
                expect(canDeleteAnySegment1).toBe(false);

                const experiment2 = experimentGenerator({
                    name:
                        'Сохранённый эксперимент с не минимальным количеством сегментов',
                    generateIds: true,
                    // tslint:disable-next-line
                    ratios: new Array(EXPERIMENT_MIN_SEGMENTS + 2).fill(10),
                });
                const canDeleteAnySegment2 = experiment2.segments.some((s) =>
                    experiment2.canDeleteSegment(s),
                );
                expect(canDeleteAnySegment2).toBe(false);
            });
        });

        it('canAddSegment', () => {
            const experiment1 = experimentGenerator({
                name: 'canAddSegment',
                // tslint:disable-next-line
                ratios: new Array(EXPERIMENT_MAX_SEGMENTS).fill(10),
            });
            expect(experiment1.canAddSegment).toBe(false);

            const experiment2 = experimentGenerator({
                name: 'canDeleteAnySegment',
                // tslint:disable-next-line
                ratios: new Array(EXPERIMENT_MAX_SEGMENTS - 1).fill(10),
            });
            expect(experiment2.canAddSegment).toBe(true);
        });
    });

    describe('action', () => {
        it('changeName works', () => {
            const experiment = experimentGenerator({
                name: 'first',
                ratios: [50, 50],
            });
            experiment.changeName('second');

            expect(experiment.name).toBe('second');
        });

        describe('addSegment', () => {
            it('works with new experiments', () => {
                const experiment = experimentGenerator({
                    name: 'name',
                    ratios: [25, 25, 25, 25],
                });

                experiment.addSegment(
                    clone(experiment.segments[experiment.segments.length - 1]),
                );

                expect(experiment.segments.length).toBe(5);
            });
            it("doesn't work when limit is reached", () => {
                const experiment = experimentGenerator({
                    name: 'name',
                    generateIds: true,
                    // tslint:disable-next-line
                    ratios: new Array(EXPERIMENT_MAX_SEGMENTS).fill(10),
                });

                expect(() => {
                    experiment.addSegment(
                        clone(
                            experiment.segments[experiment.segments.length - 1],
                        ),
                    );
                }).toThrow();
            });
            it("doesn't work on saved experiments", () => {
                const experiment = experimentGenerator({
                    name: 'name',
                    generateIds: true,
                    ratios: [25, 25, 25, 25],
                });

                expect(() => {
                    experiment.addSegment(
                        clone(
                            experiment.segments[experiment.segments.length - 1],
                        ),
                    );
                }).toThrow();
            });
        });

        describe('deleteSegment', () => {
            it('works with new experiments', () => {
                const experiment = experimentGenerator({
                    name: 'name',
                    ratios: [25, 25, 25, 25],
                });

                experiment.deleteSegment(experiment.segments[0]);

                expect(experiment.segments.length).toBe(3);
            });
            it('doesn\'t work with special "Other" type', () => {
                const experiment = experimentGenerator({
                    name: 'name',
                    ratios: [25, 25, 25, 25],
                });

                expect(() => {
                    experiment.deleteSegment(experiment.lastSegment);
                }).toThrow();
            });
            it("doesn't work on saved experiments", () => {
                const experiment = experimentGenerator({
                    name: 'name',
                    generateIds: true,
                    ratios: [25, 25, 25, 25],
                });

                expect(() => {
                    experiment.deleteSegment(experiment.segments[0]);
                }).toThrow();
                expect(() => {
                    experiment.deleteSegment(experiment.lastSegment);
                }).toThrow();
            });
        });
    });

    describe('side effects', () => {
        it("change 'Other' segment ratio while editing", () => {
            const experiment = experimentGenerator({
                name: 'name',
                ratios: [50, 50, 0],
            });

            experiment.segments[0].changeRatio(10);
            experiment.segments[1].changeRatio(10);
            expect(experiment.lastSegment.ratio).toBe(80);

            // если сумма остальных сегментов больше 100
            // (такое может быть во время редактирования)
            // должен сброситься в 0
            experiment.segments[0].changeRatio(90);
            experiment.segments[1].changeRatio(90);
            expect(experiment.lastSegment.ratio).toBe(0);
        });
    });

    // todo validationErrors
});
