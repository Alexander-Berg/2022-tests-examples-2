package ru.yandex.metrika.zkqueue.core;

import org.junit.Test;

import ru.yandex.metrika.zkqueue.api.UnitOfWork;

import static ru.yandex.metrika.zkqueue.test.ZkTesting.SYNC_TIME;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.destination1;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.payload1;

/**
 * Check rollback pool does not get saturated from operations.
 * This ensures hanging tasks are properly removed when not needed.
 */
public final class RollbackPoolSaturationTest extends BaseCoreTest {

    @Test(timeout = SYNC_TIME)
    public void checkRollbackPoolSaturation() throws Exception {
        final int threadsNum = queue1.rollbackOptions().threadNum() * 2 + 1; // Just to be sure
        for (int txIndex = 0; txIndex < threadsNum; txIndex++) {
            put1(destination1(), payload1());
            final UnitOfWork tx = queue1.newTransaction();
            tx.tryTake(destination1());
            tx.rollback(); // In current implementation this will produce a lot of waiting tasks which need to be stopped.
        }
    }

}
