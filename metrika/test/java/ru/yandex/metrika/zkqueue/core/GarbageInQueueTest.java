package ru.yandex.metrika.zkqueue.core;

import java.util.List;

import org.junit.Test;

import ru.yandex.metrika.zkqueue.api.UnitOfWork;
import ru.yandex.metrika.zkqueue.core.redelivery.ConsumeOnce;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.empty;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.destination1;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.payload1;

/**
 * Check queue operations does not leave garbage nodes
 */
public final class GarbageInQueueTest extends BaseCoreTest {

    @Test
    public void checkNothingLeftAfterCommit() throws Exception {
        put1(destination1(), payload1());

        final UnitOfWork tx = queue.newTransaction();
        tx.tryTake(destination1(), new ConsumeOnce());
        tx.commit();

        for (String path : queue.pathsWithContent(destination1())) {
            final List<String> children = curator1.getChildren().forPath(path);
            assertThat("Path " + path + " is empty after consumption", children, empty());
        }
    }

}
