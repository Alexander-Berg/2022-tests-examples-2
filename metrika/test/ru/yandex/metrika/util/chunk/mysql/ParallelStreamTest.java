package ru.yandex.metrika.util.chunk.mysql;

import java.util.Arrays;
import java.util.Collection;
import java.util.Date;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ForkJoinPool;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.junit.Ignore;

@Ignore
public class ParallelStreamTest {
    public static void main(String[] args) {
        Map<Boolean, List<Integer>> collect = Stream.of(1, 2, 3, 4).collect(Collectors.partitioningBy(x -> x > 10));
        System.out.println("collect = " + collect);
        ForkJoinPool fjp = new ForkJoinPool(5);
        List<Integer> res = null;
        try {
            res = fjp.submit(() ->
              Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16).parallelStream().map(x -> {
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                System.out.println(Thread.currentThread().getName() + " " + new Date() + ": x = " + x);
                return Arrays.asList(x * 2 + 2, x * 2);
            }).flatMap(Collection::stream).distinct().sorted().collect(Collectors.toList())).get();
        } catch (InterruptedException e) {
            e.printStackTrace();
        } catch (ExecutionException e) {
            e.printStackTrace();
        }
        System.out.println(new Date() + "res = " + res);
    }
}
