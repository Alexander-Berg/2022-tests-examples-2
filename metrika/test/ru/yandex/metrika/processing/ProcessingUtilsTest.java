package ru.yandex.metrika.processing;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Set;
import java.util.concurrent.CompletableFuture;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import org.junit.Assert;
import org.junit.Test;

import ru.yandex.metrika.util.collections.F;

import static org.hamcrest.Matchers.lessThanOrEqualTo;

public class ProcessingUtilsTest {

    @Test
    public void test() {
        var storage = IntStream.range(0, 100).boxed().collect(Collectors.toMap(F.id(), i -> "key" + i));
        var allKeys = List.copyOf(storage.keySet());
        var partSize = 10;
        AssertingFetcher<Integer, List<String>> fetcher = AssertingFetcher.withNaturalOrder(ks -> F.map(ks, storage::get), partSize);
        var result = ProcessingUtils.fetchListByPartsAsync(allKeys, fetcher, partSize).join();
        fetcher.finishCheck(allKeys);
        Assert.assertEquals(Set.copyOf(storage.values()), Set.copyOf(result));
    }


    private static class AssertingFetcher<K, T> implements Function<List<K>, CompletableFuture<T>> {

        private static <K extends Comparable<K>, T> AssertingFetcher<K, T> withNaturalOrder(Function<List<K>, T> delegate, int partSize) {
            return new AssertingFetcher<>(delegate, partSize, Comparator.naturalOrder());
        }

        private final Function<List<K>, T> delegate;
        private final int partSize;
        private final Comparator<K> keyComparator;

        private K maxPrevKey;
        private final List<K> seen = new ArrayList<>();


        private AssertingFetcher(Function<List<K>, T> delegate, int partSize, Comparator<K> keyComparator) {
            this.delegate = delegate;
            this.partSize = partSize;
            this.keyComparator = keyComparator;
        }

        @Override
        public CompletableFuture<T> apply(List<K> ks) {
            Assert.assertThat(ks.size(), lessThanOrEqualTo(partSize));
            if (maxPrevKey != null) {
                for (K k : ks) {
                    Assert.assertTrue("should be " + k + ">=" + maxPrevKey, keyComparator.compare(k, maxPrevKey) >= 0);
                }
            }
            maxPrevKey = ks.stream().max(keyComparator).orElse(null);
            seen.addAll(ks);
            return CompletableFuture.completedFuture(delegate.apply(ks));
        }

        public void finishCheck(List<K> allIds) {
            Assert.assertEquals(allIds.stream().sorted(keyComparator).collect(Collectors.toList()), seen);
        }
    }
}
