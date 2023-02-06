package ru.yandex.metrika.zkqueue.core;

import java.util.Optional;

import org.hamcrest.CoreMatchers;
import org.junit.After;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.metrika.zkqueue.api.UnitOfWork;
import ru.yandex.metrika.zkqueue.core.curator.CuratorManager;
import ru.yandex.metrika.zkqueue.core.curator.ZkOptions;
import ru.yandex.metrika.zkqueue.core.flap.ChaosMonkeyCnxnFactory;

import static java.util.Collections.singletonList;
import static org.apache.zookeeper.server.ServerCnxnFactory.ZOOKEEPER_SERVER_CNXN_FACTORY;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.metrika.zkqueue.core.flap.ChaosMonkeyCnxnFactory.FIRST_LOCK_PREFIX_PROPERTY;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.connectionTimeout;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.destination1;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.payload1;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.retryPolicy;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.sessionTimeout;

/**
 * Tricky test to check the scenario when the lock node was created, but client received an error from network flap.
 */
public final class PartialFailureTest extends BaseCoreTest {

    private ZkQueue failsOnceAfterLockCreation;

    @BeforeClass
    public static void setupClass() {
        System.setProperty(ZOOKEEPER_SERVER_CNXN_FACTORY, ChaosMonkeyCnxnFactory.class.getName());
        System.setProperty(FIRST_LOCK_PREFIX_PROPERTY, "/zq/destination-1/locks/lock-");
    }

    @Before
    public void setup() throws Exception {
        super.setup();
        failsOnceAfterLockCreation = new ZkQueue(new CuratorManager(new ZkOptions(
                server.getConnectString(), sessionTimeout(), connectionTimeout(), retryPolicy())));
        failsOnceAfterLockCreation.createIfNeeded(singletonList(destination1()));
    }

    @Test
    public void checkRollbackCanRemoveLockWhichWasCreatedOnServerButClientFailedBeforeAcknowledgingIt() throws Exception {
        put1(destination1(), payload1());

        try (UnitOfWork tx = failsOnceAfterLockCreation.newTransaction()) {
            tx.tryTake(destination1()); // Lock was created but TX is not sure who did it
        } // Rollback should still correctly remove the lock

        assertThat(take1(), CoreMatchers.equalTo(Optional.of(payload1())));
    }

    @After
    public void teardown() {
        failsOnceAfterLockCreation.close();
        super.teardown();
    }

    @AfterClass
    public static void teardownClass() {
        System.clearProperty(ZOOKEEPER_SERVER_CNXN_FACTORY);
        System.clearProperty(FIRST_LOCK_PREFIX_PROPERTY);
    }

}
