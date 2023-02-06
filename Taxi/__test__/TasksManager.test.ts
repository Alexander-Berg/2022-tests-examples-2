import path from 'path';

import {TasksManager} from '../TasksManager';
import transformString from './transformString';

const TIMEOUT = 20000;
const taskManager = new TasksManager({
    processCount: 4
});

jest.setTimeout(TIMEOUT * 3);

describe('TasksManager', () => {
    afterEach(() => {
        taskManager.cleanup();
    });

    test('No deadlocks if child failed on init', async () => {
        const tasksPromise = taskManager.splitIntoTasks(
            path.resolve(__dirname, './InitFailProcess.ts'),
            ['test'],
            []
        ).catch(() => null);

        const timeoutPromise = new Promise((resolve, reject) => {
            setTimeout(() => reject('Timeout'), TIMEOUT);
        });

        await Promise.race([
            tasksPromise,
            timeoutPromise
        ]);
    });

    test('No deadlocks if child failed on run', async () => {
        const tasksPromise = taskManager.splitIntoTasks(
            path.resolve(__dirname, './RunFailProcess.ts'),
            ['test'],
            []
        );

        const timeoutPromise = new Promise((resolve, reject) => {
            setTimeout(() => reject('Timeout'), TIMEOUT);
        });

        await Promise.race([
            tasksPromise,
            timeoutPromise
        ]);
    });

    test('Data correctly processed', async () => {
        const data = ['1', '2', '3', '4'];

        const tasksPromise = taskManager.splitIntoTasks<string, string[], string[]>(
            path.resolve(__dirname, './TestProcess.ts'),
            data,
            [path.resolve(__dirname, 'transformString.ts')]
        );

        const timeoutPromise = new Promise<string[]>((resolve, reject) => {
            setTimeout(() => reject('Timeout'), TIMEOUT);
        });

        const results = await Promise.race([
            tasksPromise,
            timeoutPromise
        ]);

        const expected = data.map(transformString);
        results.forEach(res => {
            expect(expected).toContain(res);
        });
    });
});
