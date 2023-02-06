package ru.yandex.metrika.util.concurrent.pool;

import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Future;
import java.util.function.Predicate;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import org.apache.commons.lang3.tuple.Pair;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.MatcherAssert.assertThat;

/**
 * Created by graev on 07/11/2016.
 */
public class BoundedConnectionPoolTest {

    private BoundedConnectionPool<Key, Connection> connectionPool;

    private static final int MAX_SIZE = 10;

    private static final long CLEAN_PERIOD = 300;

    @Before
    public void setUp() {
        connectionPool = createConnectionPool(null);
    }

    @After
    public void teardown() throws InterruptedException {
        if (connectionPool != null) {
            connectionPool.close();
        }
    }

    @Test
    public void testSubsequentBorrow() {
        final Key key = new Key();
        final Connection c = connectionPool.borrowOrCreate(key);
        assertThat(c, equalTo(connectionPool.borrowOrCreate(key)));
        assertThat(c.closed, equalTo(false));
    }

    @Test
    public void testReleaseWithoutBorrow() {
        final Key key = new Key();
        connectionPool.release(key);
    }

    @Test
    public void testBorrowedAreNotReleased() throws InterruptedException {
        final Map<Key, Connection> connectionByKey = IntStream.rangeClosed(1, MAX_SIZE * 2)
                .mapToObj(i -> new Key())
                .map(k -> Pair.of(k, connectionPool.borrowOrCreate(k)))
                .collect(Collectors.toMap(Pair::getLeft, Pair::getRight));

        Thread.sleep(CLEAN_PERIOD * 3);
        assertThat(connectionPool.currentSize(), equalTo(MAX_SIZE * 2));

        final int closed = (int) connectionByKey.values().stream().filter(Connection::isClosed).count();
        assertThat(closed, equalTo(0));
    }

    @Test
    public void testReleasedAreCollected() throws InterruptedException {
        final Map<Key, Connection> connectionByKey = IntStream.rangeClosed(1, MAX_SIZE * 2)
                .mapToObj(i -> new Key())
                .map(k -> Pair.of(k, connectionPool.borrowOrCreate(k)))
                .peek(p -> connectionPool.release(p.getKey()))
                .collect(Collectors.toMap(Pair::getLeft, Pair::getRight));

        Thread.sleep(CLEAN_PERIOD * 3);
        assertThat(connectionPool.currentSize(), equalTo(MAX_SIZE));

        final int closed = (int) connectionByKey.values().stream().filter(Connection::isClosed).count();
        assertThat(closed, equalTo(MAX_SIZE));
    }

    @Test
    public void testEvictPredicate() throws InterruptedException {
        BoundedConnectionPool<Key, Connection> connectionPool = createConnectionPool(conn -> true);
        final Map<Key, Connection> connectionByKey = IntStream.rangeClosed(1, MAX_SIZE)
                .mapToObj(i -> new Key())
                .map(k -> Pair.of(k, connectionPool.borrowOrCreate(k)))
                .collect(Collectors.toMap(Pair::getLeft, Pair::getRight));

        Thread.sleep(CLEAN_PERIOD * 3);
        assertThat(connectionPool.currentSize(), equalTo(0));

        final int closed = (int) connectionByKey.values().stream().filter(Connection::isClosed).count();
        assertThat(closed, equalTo(MAX_SIZE));
    }

    private static class Key {
    }

    private static class Connection {

        private volatile boolean closed = false;

        public void close() {
            closed = true;
        }

        public boolean isClosed() {
            return closed;
        }
    }

    private static BoundedConnectionPool<Key, Connection> createConnectionPool(Predicate<Connection> evictPredicate) {
        return new BoundedConnectionPool<>(new ConnectionManager<>() {
            @Override
            public Connection create(Key key) {
                return new Connection();
            }

            @Override
            public Future<Void> destroy(Connection connection) {
                connection.close();
                return CompletableFuture.completedFuture(null);
            }
        }, MAX_SIZE, evictPredicate, CLEAN_PERIOD);
    }
}
