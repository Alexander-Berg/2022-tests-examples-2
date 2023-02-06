package ru.yandex.metrika.zkqueue.core;

import java.util.Optional;

import org.junit.Test;

import ru.yandex.metrika.zkqueue.api.UnitOfWork;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.destination1;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.payload1;

/**
 * Check try-with-resources block for queue transactions
 */
public final class CloseTxTest extends BaseCoreTest {

    @Test
    public void checkClosingRollbacks() throws Exception {
        put1(destination1(), payload1());

        try (UnitOfWork tx = queue1.newTransaction()) {
            final Optional<String> item = tx.tryTake(destination1());
            assertThat(item, equalTo(Optional.of(payload1())));
        }

        assertThat(take1(), equalTo(Optional.of(payload1())));
    }

    @Test
    public void checkClosingDoesNotFailIfCommitted() throws Exception {
        put1(destination1(), payload1());

        try (UnitOfWork tx = queue1.newTransaction()) {
            final Optional<String> item = tx.tryTake(destination1());
            assertThat(item, equalTo(Optional.of(payload1())));
            tx.commit();
        }

        assertThat(take1(), equalTo(Optional.empty()));
    }

    @Test
    public void checkClosingDoesNotFailIfRolledBack() throws Exception {
        put1(destination1(), payload1());

        try (UnitOfWork tx = queue1.newTransaction()) {
            final Optional<String> item = tx.tryTake(destination1());
            assertThat(item, equalTo(Optional.of(payload1())));
            tx.rollback();
        }

        assertThat(take1(), equalTo(Optional.of(payload1())));
    }

}
