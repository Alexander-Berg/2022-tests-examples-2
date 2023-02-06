package ru.yandex.metrika.zkqueue.core;

import java.util.Optional;

import org.junit.Test;

import ru.yandex.metrika.zkqueue.api.ConsumeTimes;
import ru.yandex.metrika.zkqueue.api.UnitOfWork;
import ru.yandex.metrika.zkqueue.api.redelivery.ConsumingPolicy;
import ru.yandex.metrika.zkqueue.core.redelivery.ConsumeOnce;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.destination1;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.payload1;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.payload2;

/**
 * Check various consuming policies.
 */
public final class RedeliveryTest extends BaseCoreTest {

    @Test
    public void checkOnceOnlyMessaging() throws Exception {
        put1(destination1(), payload1());

        final UnitOfWork tx = queue.newTransaction();
        final Optional<String> element1 = tx.tryTake(destination1(), new ConsumeOnce());
        assertThat(element1, equalTo(Optional.of(payload1())));
        tx.rollback();

        final UnitOfWork tx2 = queue.newTransaction();
        final Optional<String> element2 = tx2.tryTake(destination1(), new ConsumeOnce());

        assertThat(element2, equalTo(Optional.empty()));
    }

    @Test
    public void checkConstantRedeliverCount() throws Exception {
        put1(destination1(), payload1());

        final int someFixedAmount = 10;
        final ConsumingPolicy policy = new ConsumeTimes(someFixedAmount);

        for (int attempt = 1; attempt <= someFixedAmount; attempt++) {
            final UnitOfWork tx = queue.newTransaction();
            final Optional<String> consumed = tx.tryTake(destination1(), policy);
            assertThat(consumed, equalTo(Optional.of(payload1())));
            tx.rollback();
        }

        final UnitOfWork tx2 = queue.newTransaction();
        final Optional<String> element = tx2.tryTake(destination1(), policy);

        assertThat(element, equalTo(Optional.empty()));
    }

    @Test
    public void checkDiscardedItemDoesNotGetInTheWay() throws Exception {
        put1(destination1(), payload1());

        final UnitOfWork tx1 = queue.newTransaction();
        tx1.tryTake(destination1());
        tx1.rollback();

        put1(destination1(), payload2());
        final UnitOfWork tx2 = queue.newTransaction();
        final Optional<String> item = tx2.tryTake(destination1(), new ConsumeOnce()); // Discard the first element

        assertThat(item, equalTo(Optional.of(payload2())));
    }

}
