package ru.yandex.metrika.zkqueue.core;

import java.util.Optional;

import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.ExpectedException;

import ru.yandex.metrika.zkqueue.api.UnitOfWork;
import ru.yandex.metrika.zkqueue.api.exception.ZkQueueIllegalStateException;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.destination1;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.payload1;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.payload2;

/**
 * Check basic transaction guarantees
 */
public final class UnitOfWorkTest extends BaseCoreTest {

    @Rule
    public ExpectedException expectedException = ExpectedException.none();

    @Test
    public void checkTxCommit() throws Exception {
        final UnitOfWork tx = queue.newTransaction();
        tx.put(destination1(), payload1());
        tx.commit();

        assertThat(take1(), equalTo(Optional.of(payload1())));
    }

    @Test
    public void checkTxRollback() throws Exception {
        final UnitOfWork tx = queue.newTransaction();
        tx.put(destination1(), payload1());
        tx.rollback();

        assertThat(take1(), equalTo(Optional.empty()));
    }

    @Test
    public void checkNoDirtyReads() throws Exception {
        final UnitOfWork tx = queue.newTransaction();
        tx.put(destination1(), payload1());

        assertThat(take1(), equalTo(Optional.empty()));
    }

    @Test
    public void checkElementsLocking() throws Exception {
        put1(destination1(), payload1());

        final UnitOfWork tx = queue.newTransaction();
        final Optional<String> element = tx.tryTake(destination1());

        final UnitOfWork tx2 = queue.newTransaction();
        final Optional<String> empty = tx2.tryTake(destination1());

        assertThat(element, equalTo(Optional.of(payload1())));
        assertThat(empty, equalTo(Optional.empty()));
    }

    @Test
    public void checkElementsUnlocking() throws Exception {
        put1(destination1(), payload1());

        final UnitOfWork tx = queue.newTransaction();
        tx.tryTake(destination1());
        tx.rollback();

        assertThat(take1(), equalTo(Optional.of(payload1())));
    }

    @Test
    public void checkTakeAndPut() throws Exception {
        put1(destination1(), payload1());

        final UnitOfWork tx = queue.newTransaction();
        final Optional<String> payload = tx.tryTake(destination1());
        tx.put(destination1(), payload2());
        tx.commit();

        final Optional<String> payload2 = take1();
        final Optional<String> empty = take1();

        assertThat(payload, equalTo(Optional.of(payload1())));
        assertThat(payload2, equalTo(Optional.of(payload2())));
        assertThat(empty, equalTo(Optional.empty()));
    }

    @Test
    public void checkEmptyCommit() throws Exception {
        final UnitOfWork tx = queue.newTransaction();

        tx.commit();

        assertThat(take1(), equalTo(Optional.empty()));
    }

    @Test
    public void checkTxReuseOnPut() throws Exception {
        final UnitOfWork tx = queue.newTransaction();
        tx.commit();

        expectedException.expect(ZkQueueIllegalStateException.class);
        tx.put(destination1(), payload1());
    }

    @Test
    public void checkTxReuseOnTake() throws Exception {
        final UnitOfWork tx = queue.newTransaction();
        tx.commit();

        expectedException.expect(ZkQueueIllegalStateException.class);
        tx.tryTake(destination1());
    }

    @Test
    public void checkTxReuseOnPutAfterRollback() throws Exception {
        final UnitOfWork tx = queue.newTransaction();
        tx.rollback();

        expectedException.expect(ZkQueueIllegalStateException.class);
        tx.put(destination1(), payload1());
    }

    @Test
    public void checkTxReuseOnTakeAfterRollback() throws Exception {
        final UnitOfWork tx = queue.newTransaction();
        tx.rollback();

        expectedException.expect(ZkQueueIllegalStateException.class);
        tx.tryTake(destination1());
    }

}
