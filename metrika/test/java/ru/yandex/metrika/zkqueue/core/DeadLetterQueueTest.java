package ru.yandex.metrika.zkqueue.core;

import com.google.common.collect.Iterables;
import org.apache.curator.utils.ZKPaths;
import org.junit.Test;

import ru.yandex.metrika.zkqueue.api.UnitOfWork;
import ru.yandex.metrika.zkqueue.api.redelivery.ConsumingPolicy;
import ru.yandex.metrika.zkqueue.core.redelivery.AlwaysConsume;
import ru.yandex.metrika.zkqueue.core.redelivery.ConsumeOnce;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.destination1;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.payload1;

/**
 * Check that failing messages go to DLQ with respect to {@link ConsumingPolicy}
 */
public final class DeadLetterQueueTest extends BaseCoreTest {

    @Test
    public void checkWhenElementRemainsNothingGetsToDlq() throws Exception {
        put1(destination1(), payload1());
        final UnitOfWork tx = queue.newTransaction();
        tx.tryTake(destination1(), new AlwaysConsume());
        tx.rollback();


        assertThat(curator1.getChildren().forPath(dlqPath()), empty());
    }

    @Test
    public void checkDlqPayload() throws Exception {
        put1(destination1(), payload1());
        final UnitOfWork tx = queue.newTransaction();
        tx.tryTake(destination1(), new ConsumeOnce());
        tx.rollback();

        // We need to 'consume' the item to be discarded to DLQ
        final UnitOfWork tx2 = queue.newTransaction();
        tx2.tryTake(destination1(), new ConsumeOnce());
        tx2.rollback();

        final String dlqNode = Iterables.getOnlyElement(curator1.getChildren().forPath(dlqPath()));
        final byte[] bytes = curator1.getData().forPath(ZKPaths.makePath(dlqPath(), dlqNode));

        assertThat(new String(bytes), equalTo(payload1()));
    }

    private String dlqPath() {
        return ZKPaths.makePath("/zq", destination1(), "dlq");
    }

}
