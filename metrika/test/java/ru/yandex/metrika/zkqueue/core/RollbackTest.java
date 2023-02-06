package ru.yandex.metrika.zkqueue.core;

import java.util.Optional;

import org.hamcrest.MatcherAssert;
import org.hamcrest.Matchers;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.ExpectedException;

import ru.yandex.metrika.zkqueue.api.UnitOfWork;

import static ru.yandex.metrika.zkqueue.test.ZkTesting.SYNC_TIME;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.destination1;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.payload1;

/**
 * Check rollback guarantees.
 */
public final class RollbackTest extends BaseCoreTest {

    @Rule
    public ExpectedException expectedException = ExpectedException.none();

    @Test(timeout = SYNC_TIME)
    public void checkEmptyRollback() throws Exception {
        final UnitOfWork tx = queue1.newTransaction();
        tx.rollback();

        checkElementsAvailability(0);
    }

    @Test(timeout = SYNC_TIME)
    public void checkRollbacking2Elements() throws Exception {
        put1(destination1(), payload1());
        put1(destination1(), payload1());

        final UnitOfWork tx = queue1.newTransaction();
        tx.tryTake(destination1());
        tx.tryTake(destination1());
        tx.rollback();

        checkElementsAvailability(2);
    }

    @Test(timeout = SYNC_TIME)
    public void checkRollbackAfterExpiration() throws Exception {
        put1(destination1(), payload1());

        final UnitOfWork tx = queue1.newTransaction();
        tx.tryTake(destination1());
        expireSession1();
        tx.rollback();

        checkElementsAvailability(1);
    }

    @Test(timeout = SYNC_TIME)
    public void checkRollbackAfterDisconnection() throws Exception {
        put1(destination1(), payload1());

        final UnitOfWork tx = queue1.newTransaction();
        tx.tryTake(destination1());
        disconnectClient1();
        tx.rollback();

        checkElementsAvailability(1);
    }

    @Test(timeout = SYNC_TIME)
    public void checkRollbackAfterExpirationAndThenDisconnection() throws Exception {
        put1(destination1(), payload1());

        final UnitOfWork tx = queue1.newTransaction();
        tx.tryTake(destination1());
        expireSession1();
        disconnectClient1(); // Nice.
        tx.rollback();

        checkElementsAvailability(1);
    }

    @Test(timeout = SYNC_TIME)
    public void checkRollbackIsPossibleWithDeadServer() throws Exception {
        put1(destination1(), payload1());

        final UnitOfWork tx = queue1.newTransaction();
        tx.tryTake(destination1());
        killServer1();
        tx.rollback();
    }

    @Test
    public void checkCommitDoesNotHangOnDeadServer() throws Exception {
        put1(destination1(), payload1());

        try (UnitOfWork tx = queue1.newTransaction()) {
            tx.tryTake(destination1());
            killServer1();

            expectedException.expect(Exception.class);

            tx.commit();
        }
    }

    /**
     * Check that queue contains exactly {@code amount} elements
     */
    private void checkElementsAvailability(int amount) throws Exception {
        for (int attempt = 1; attempt <= amount; attempt++) {
            final Optional<String> empty = take2();
            MatcherAssert.assertThat(empty, Matchers.equalTo(Optional.of(payload1())));
        }

        final Optional<String> empty = take2();
        MatcherAssert.assertThat(empty, Matchers.equalTo(Optional.empty()));
    }


}
