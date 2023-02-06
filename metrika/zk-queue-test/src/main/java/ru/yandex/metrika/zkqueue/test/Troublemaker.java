package ru.yandex.metrika.zkqueue.test;

import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

import org.apache.curator.framework.CuratorFramework;
import org.apache.curator.framework.state.ConnectionState;
import org.apache.curator.framework.state.ConnectionStateListener;
import org.apache.curator.test.TestingServer;
import org.apache.zookeeper.Watcher;
import org.apache.zookeeper.ZooKeeper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import static java.util.concurrent.TimeUnit.MILLISECONDS;
import static org.awaitility.Awaitility.await;

/**
 * Emulate bad things with zookeeper cluster for testing purposes
 */
public final class Troublemaker {

    /**
     * Wait until zookeeper is connected
     */
    private static final long CONNECTION_WAIT_TIME = 2000L;

    /**
     * Emulate server death
     */
    public static void stopServer(TestingServer server) {
        try {
            server.stop();
        } catch (Exception e) {
            throw new RuntimeException("Server stop was unsuccessful", e);
        }
    }

    /**
     * Emulate connection closing by client
     */
    public static void disconnectClient(CuratorFramework curator) {
        curator.close();
    }

    /**
     * Emulate zookeeper server restart
     */
    public static void restartServer(TestingServer server) {
        try {
            server.restart();
        } catch (Exception e) {
            throw new RuntimeException("Server restart gone wrong", e);
        }
    }

    /**
     * Expire current session of given curator client without explicitly closing it.
     * This method imitates session expiration, but works instantaneously.
     * <p>
     * This is done in a weird way
     * <ul>
     * <li>create another session with the same session id and password</li>
     * <li>close it</li>
     * <li>wait until current client gets notified about session expiration</li>
     * </ul>
     * <p>
     * The same approach is used in helix tests: http://bit.ly/2iZxzSW
     */
    public static void expireCuratorSession(CuratorFramework curator) {
        try {
            final WaitLost expirationListener = new WaitLost();
            curator.getConnectionStateListenable().addListener(expirationListener);
            final String connectionString = curator.getZookeeperClient().getCurrentConnectionString();
            expireZkSession(curator.getZookeeperClient().getZooKeeper(), connectionString);
            await().atMost(2 * curator.getZookeeperClient().getLastNegotiatedSessionTimeoutMs(), MILLISECONDS)
                    .until(expirationListener::lost);
        } catch (Exception e) {
            throw new RuntimeException("Session expiration was not performed", e);
        }
    }

    /**
     * Expire given zookeeper client
     */
    private static void expireZkSession(ZooKeeper client, String connectionString) {
        try {
            final Watcher dummyWatch = (e) -> {
            };
            final ZooKeeper duplicated = new ZooKeeper(connectionString, client.getSessionTimeout(),
                    dummyWatch, client.getSessionId(), client.getSessionPasswd());

            await().atMost(CONNECTION_WAIT_TIME, TimeUnit.MILLISECONDS)
                    .until(() -> duplicated.getState() == ZooKeeper.States.CONNECTED);

            duplicated.close();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * Waiter for 'session expired' connection state
     */
    private static class WaitLost implements ConnectionStateListener {

        private static final Logger LOG = LoggerFactory.getLogger(WaitLost.class);

        private final AtomicBoolean hasLost;

        WaitLost() {
            this.hasLost = new AtomicBoolean();
        }

        @Override
        public void stateChanged(CuratorFramework client, ConnectionState newState) {
            LOG.info("Received " + newState + " from ZK");

            if (newState == ConnectionState.LOST) {
                hasLost.set(true);
            }
        }

        boolean lost() {
            return hasLost.get();
        }
    }


}
