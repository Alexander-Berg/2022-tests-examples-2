package ru.yandex.autotests.morda.rules.errorcollector;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 06/04/15
 */
public class HierarchicalErrorCollector {
    private static final long DEFAULT_TIMEOUT = 120;
    private List<List<Runnable>> checks;
    private List<HierarchicalErrorCollector> collectors;
    private final List<Throwable> errors;

    public HierarchicalErrorCollector() {
        checks = new ArrayList<>();
        collectors = new ArrayList<>();
        errors = new ArrayList<>();
    }

    public static HierarchicalErrorCollector collector() {
        return new HierarchicalErrorCollector();
    }

    public void collect() {
        ExecutorService executorService = Executors.newFixedThreadPool(10);

        for (List<Runnable> list : checks) {
            final List<Throwable> errors = new ArrayList<>();
            final CountDownLatch countDownLatch = new CountDownLatch(list.size());

            list.stream().forEach((runnable) ->
                    executorService.execute(checkRunnable(errors, runnable, countDownLatch)));

            try {
                countDownLatch.await(DEFAULT_TIMEOUT, TimeUnit.SECONDS);
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }

            if (errors.size() > 0) {
                synchronized (this.errors) {
                    this.errors.addAll(errors);
                }
                return;
            }
        }

        collectors.stream().forEach((collector) -> executorService.execute(collector::collect));

        try {
            executorService.shutdown();
            executorService.awaitTermination(DEFAULT_TIMEOUT, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }

    }

    public List<Throwable> getErrors() {
        final List<Throwable> errors = new ArrayList<>();

        errors.addAll(this.errors);

        collectors.stream().forEachOrdered((collector) -> errors.addAll(collector.getErrors()));

        return errors;
    }

    public HierarchicalErrorCollector check(Runnable... checks) {
        if (checks.length > 0) {
            this.checks.add(asList(checks));
        }
        return this;
    }

    public HierarchicalErrorCollector check(HierarchicalErrorCollector... collectors) {
        this.collectors.addAll(asList(collectors));
        return this;
    }

    private Runnable checkRunnable(List<Throwable> errors, Runnable runnable, CountDownLatch countDownLatch) {
        return () -> {
            try {
                runnable.run();
            } catch (Throwable e) {
                synchronized (errors) {
                    errors.add(e);
                }
            } finally {
                countDownLatch.countDown();
            }
        };
    }
}
