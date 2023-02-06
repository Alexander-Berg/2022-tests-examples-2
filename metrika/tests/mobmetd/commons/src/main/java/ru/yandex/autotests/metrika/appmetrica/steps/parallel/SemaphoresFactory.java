package ru.yandex.autotests.metrika.appmetrica.steps.parallel;

import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableList;

import java.util.List;

import static java.lang.String.format;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.HazelcastFactory.hazelcastInstance;

/**
 * Достаем экземпляр семафоров, который зависит от того, как мы запустили тесты
 */
final class SemaphoresFactory {

    /**
     * Пока что имеем 4 семафора для 4-ёх слоёв mtmoblog соответственно.
     */
    private static final List<Integer> ALL_SEMAPHORE_IDS = ImmutableList.of(1, 2, 3, 4);

    private static Semaphores instance;

    static synchronized Semaphores semaphoresInstance() {
        if (instance != null) {
            return instance;
        }

        return (instance = createSemaphores());
    }

    private static Semaphores createSemaphores() {
        return isRunningOnAero() ?
                new HazelcastSemaphores(hazelcastInstance(), ALL_SEMAPHORE_IDS) :
                new LocalSemaphores(ALL_SEMAPHORE_IDS);
    }

    /**
     * Проверка того, что тест запущен в акве и нам доступен Hazelcast
     */
    private static boolean isRunningOnAero() {
        return System.getProperty("aero.pack.uuid") != null &&
                System.getProperty("aero.suite.uuid") != null &&
                System.getProperty("aero.suite.name") != null;
    }

    public static void checkSemaphoreId(Integer semaphoreId) {
        Preconditions.checkArgument(
                ALL_SEMAPHORE_IDS.contains(semaphoreId),
                format("Invalid semaphore id: %s. Possible semaphore ids: %s", semaphoreId, ALL_SEMAPHORE_IDS));
    }

    public static List<Integer> getAllSemaphoreIds() {
        return ALL_SEMAPHORE_IDS;
    }

}
