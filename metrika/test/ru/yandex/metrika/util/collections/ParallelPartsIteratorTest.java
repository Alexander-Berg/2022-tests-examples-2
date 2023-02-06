package ru.yandex.metrika.util.collections;

import java.util.HashSet;
import java.util.Iterator;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import com.google.common.collect.Sets;
import org.junit.Test;

import static org.assertj.core.api.Assertions.assertThat;

public class ParallelPartsIteratorTest {

    private static final int numIterations = 10;
    private static final int iteratorSizePerIteration = 10;
    private static final int poolSize = 3;
    private static final int bufferSize = 3;

    @Test
    public void justWorks() {
        ParallelPartsIterator<Integer> it = new ParallelPartsIterator<>(numIterations, poolSize, bufferSize) {
            @Override
            protected Iterator<Integer> doGetNextPart(int iteration) {
                return IntStream.range(0, iteratorSizePerIteration).map(i -> iteratorSizePerIteration*iteration + i).iterator();
            }
        };

        Set<Integer> ints = Sets.newHashSet();
        while (it.hasNext()) {
            ints.add(it.next());
        }
        assertThat(ints).isEqualTo(IntStream.range(0, 100).boxed().collect(Collectors.toSet()));
    }

    @Test
    public void callsDoGetNextPartOnlyAsNeeded() throws InterruptedException {
        AtomicInteger nextPartCalls = new AtomicInteger(0);
        ParallelPartsIterator<Integer> it = new ParallelPartsIterator<>(numIterations, poolSize, bufferSize) {
            @Override
            protected Iterator<Integer> doGetNextPart(int iteration) {
                nextPartCalls.incrementAndGet();
                return IntStream.range(0, iteratorSizePerIteration).map(i -> iteratorSizePerIteration*iteration + i).iterator();
            }
        };

        Thread.sleep(200);

        assertThat(nextPartCalls.get()).isEqualTo(poolSize + bufferSize);

        it.next();
        Thread.sleep(200);
        assertThat(nextPartCalls.get()).isEqualTo(poolSize + bufferSize + 1);

        for (int i = 0; i < iteratorSizePerIteration - 1;i++) {
            it.next();
        }
        Thread.sleep(200);
        assertThat(nextPartCalls.get()).isEqualTo(poolSize + bufferSize + 1);

        while(it.hasNext()) {
            it.next();
        }
        Thread.sleep(200);
        assertThat(nextPartCalls.get()).isEqualTo(numIterations);
    }

    @Test
    public void shortCutsAndThrowsError() throws InterruptedException {
        AtomicInteger nextPartCalls = new AtomicInteger(0);
        final ParallelPartsIterator<Integer> it = new ParallelPartsIterator<>(numIterations, poolSize, bufferSize) {
            @Override
            protected Iterator<Integer> doGetNextPart(int iteration) {
                nextPartCalls.incrementAndGet();
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }
                if (iteration%2 == 0) {
                    throw new RuntimeException("thrown in doGetNextPart");
                }

                return IntStream.range(1, iteratorSizePerIteration).mapToObj(i -> iteratorSizePerIteration * iteration + i).toList().iterator();
            }
        };

        Set<Integer> ints = new HashSet<>();
        try {
            while (it.hasNext()) {
                Thread.sleep(100);
                ints.add(it.next());
            }
        } catch (RuntimeException e) {
            assertThat(ints.size()).isLessThan(numIterations * iteratorSizePerIteration);
            assertThat(nextPartCalls.get()).isLessThan(numIterations);
            return;
        }

        throw new RuntimeException("exception must have been thrown");
    }

}
