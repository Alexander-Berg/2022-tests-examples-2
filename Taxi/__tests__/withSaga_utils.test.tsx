import {LoadedTasksCountsMapType} from '../types';
import {
    runFork,
    loadTask,
    disposeTask,
    disposeTasksOnPage,
    testSaga,
    getLoadedTasksCountsMap,
    clearLoadedTasks,
} from '../utils';

const resultTestWithSagaFlow: LoadedTasksCountsMapType = {
    testLoadId_1: undefined,
    testLoadId_2: 1,
    testLoadId_3: 2,
};

test('withSaga utils (runFork, loadTask, disposeTask) should manage map of sagas', () => {
    const sagaInstance = runFork(testSaga);
    const testLoadId_1 = 'testLoadId_1';
    const testLoadId_2 = 'testLoadId_2';
    const testLoadId_3 = 'testLoadId_3';

    loadTask({
        loadId: testLoadId_1,
        saga: sagaInstance,
        args: null,
    });

    disposeTask(testLoadId_1);

    loadTask({
        loadId: testLoadId_2,
        saga: sagaInstance,
        args: null,
    });

    loadTask({
        loadId: testLoadId_2,
        saga: sagaInstance,
        args: null,
    });

    disposeTask(testLoadId_2);

    loadTask({
        loadId: testLoadId_3,
        saga: sagaInstance,
        args: null,
    });

    loadTask({
        loadId: testLoadId_3,
        saga: sagaInstance,
        args: null,
    });

    disposeTask(testLoadId_3);

    loadTask({
        loadId: testLoadId_3,
        saga: sagaInstance,
        args: null,
    });

    disposeTask(testLoadId_3);

    loadTask({
        loadId: testLoadId_3,
        saga: sagaInstance,
        args: null,
    });

    expect(getLoadedTasksCountsMap()).toEqual(resultTestWithSagaFlow);

    clearLoadedTasks();
});

const resultTestDisposeTasksOnPage: LoadedTasksCountsMapType = {
    testLoadId_1: undefined,
    testLoadId_2: 1,
    testLoadId_3: undefined,
};

test('withSaga util "disposeTasksOnPage" should clear sagas without flag "isRoot"', () => {
    const sagaInstance = runFork(testSaga);
    const testLoadId_1 = 'testLoadId_1';
    const testLoadId_2 = 'testLoadId_2';
    const testLoadId_3 = 'testLoadId_3';

    loadTask({
        loadId: testLoadId_1,
        saga: sagaInstance,
        args: null,
    });

    loadTask({
        loadId: testLoadId_2,
        saga: sagaInstance,
        args: null,
        isRoot: true,
    });

    loadTask({
        loadId: testLoadId_3,
        saga: sagaInstance,
        args: null,
    });

    disposeTasksOnPage();

    expect(getLoadedTasksCountsMap()).toEqual(resultTestDisposeTasksOnPage);

    clearLoadedTasks();
});
