import Queue from '../execution-queue';

describe('utils:execution-queue', () => {
    const TIMEOUT_PROGRESS_UPDATE = 100;
    const TIMEOUT_TEST = 300;

    const RESULT = 'RESULT';
    const ERROR = new Error();
    const POOL_SIZE = 2;
    const PROGRESS = 50;

    let abortFuncs;

    const createTask = (id, result, resultTimeout) => {
        const abort = jest.fn();
        abortFuncs[id] = abort;

        return {
            id,
            execute: jest.fn(updateProgress => {
                updateProgress(PROGRESS);

                let promise = new Promise((resolve, reject) => {
                    if (result !== undefined) {
                        const end = () => {
                            if (result) {
                                resolve(RESULT);
                            } else {
                                reject(ERROR);
                            }
                        };

                        if (resultTimeout) {
                            setTimeout(
                                end,
                                resultTimeout
                            );
                        } else {
                            end();
                        }
                    }
                });

                promise.abort = abort;

                return promise;
            }),
            onStart: jest.fn(),
            onDone: jest.fn(),
            onError: jest.fn(),
            onProgress: jest.fn()
        };
    };

    const queue = new Queue({
        poolSize: POOL_SIZE,
        progressUpdateInterval: TIMEOUT_PROGRESS_UPDATE
    });

    beforeEach(() => {
        abortFuncs = {};

        queue.reset();
    });

    test('Вызывает обработку задания в порядке помещения в очередь, но не более чем poolSize', () => {
        const TASKS_COUNT = 10;
        const tasks = [];

        for (let id = 0; id < TASKS_COUNT; id++) {
            const task = createTask(id);

            tasks.push(task);
            queue.add(task);
        }

        expect(tasks[0].execute).toHaveBeenCalled();
        expect(tasks[1].execute).toHaveBeenCalled();
        expect(queue.queue.length).toEqual(TASKS_COUNT - POOL_SIZE);
        expect(Object.keys(queue.tasks).length).toEqual(TASKS_COUNT);

        expect(queue.progressEmitter.get(0)).toEqual(PROGRESS);
        expect(queue.progressEmitter.get(1)).toEqual(PROGRESS);
    });

    test('Удаляет из очереди задания (тест тех, которые не исполняются)', () => {
        const TASKS_COUNT = 10;

        for (let id = 0; id < TASKS_COUNT; id++) {
            const task = createTask(id);

            queue.add(task);
        }

        queue.remove(9);

        expect(queue.queue).toEqual([2, 3, 4, 5, 6, 7, 8]);
    });

    test('Удаляет из очереди задания, которые исполняются, вызывая у них abort, и переходя дальше по очереди', () => {
        const TASKS_COUNT = 10;
        const DELETE_INDEX = 1;
        const tasks = [];

        for (let id = 0; id < TASKS_COUNT; id++) {
            const task = createTask(id);

            tasks.push(task);
            queue.add(task);
        }

        queue.remove(DELETE_INDEX);

        expect(tasks[0].execute).toHaveBeenCalled();
        expect(tasks[1].execute).toHaveBeenCalled();
        expect(tasks[2].execute).toHaveBeenCalled();
        expect(queue.queue).toEqual([3, 4, 5, 6, 7, 8, 9]);
        expect(abortFuncs[DELETE_INDEX]).toHaveBeenCalled();
    });

    test('После успеха выполнения задачи вызывается onTaskDone', done => {
        const RESULT_TIMEOUT = 3 * TIMEOUT_PROGRESS_UPDATE;
        const TASK = createTask(0, true, RESULT_TIMEOUT);

        queue.add(TASK);

        setTimeout(
            () => {
                expect(TASK.onStart).toHaveBeenCalled();
                expect(queue.queue.length).toEqual(0);
                expect(TASK.onProgress).toHaveBeenCalledWith(PROGRESS);
                expect(TASK.onProgress).toHaveBeenCalledTimes(1);
                expect(TASK.onDone).toHaveBeenCalledWith(RESULT);

                done();
            },
            TIMEOUT_TEST + RESULT_TIMEOUT
        );
    });

    test('После фейла выполнения задачи вызывается onTaskError', done => {
        const TASK = createTask(0, false);

        queue.add(TASK);

        setTimeout(
            () => {
                expect(TASK.onStart).toHaveBeenCalled();
                expect(queue.queue.length).toEqual(0);
                expect(TASK.onError).toHaveBeenCalledWith(PROGRESS, ERROR);

                done();
            },
            TIMEOUT_TEST
        );
    });
});
