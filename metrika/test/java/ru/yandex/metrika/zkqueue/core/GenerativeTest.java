package ru.yandex.metrika.zkqueue.core;

import java.util.List;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Future;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import org.junit.Test;

import static com.google.common.collect.ImmutableSet.copyOf;
import static java.util.concurrent.Executors.newFixedThreadPool;
import static java.util.stream.Collectors.toList;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.destination1;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.payload1;

/**
 * Try to create threads contention on producing/consuming.
 * Check not race conditions occurred.
 */
public final class GenerativeTest extends BaseCoreTest {

    @Test
    public void checkThreadsContention() throws InterruptedException, ExecutionException {
        final int nodes = 1000;
        final int threads = 20;

        final List<String> elements = IntStream.rangeClosed(1, nodes)
                .mapToObj(i -> payload1() + i)
                .collect(toList());

        final List<Callable<Void>> putTasks = elements.stream()
                .map(p -> ((Callable<Void>) (() -> {
                    put1(destination1(), p);
                    return null;
                })))
                .collect(Collectors.toList());

        final Set<String> taken = ConcurrentHashMap.newKeySet();
        final ExecutorService pool = newFixedThreadPool(threads);
        final List<Future<Void>> putFutures = pool.invokeAll(putTasks);

        for (Future<Void> future : putFutures) {
            future.get();
        }

        final List<Callable<String>> takeTasks = IntStream.rangeClosed(1, nodes)
                .mapToObj(i -> ((Callable<String>) (() -> take1().get())))
                .collect(Collectors.toList());
        final List<Future<String>> takeFutures = pool.invokeAll(takeTasks);

        for (Future<String> future : takeFutures) {
            taken.add(future.get());
        }

        assertThat(copyOf(taken), equalTo(copyOf(elements)));
    }

}
