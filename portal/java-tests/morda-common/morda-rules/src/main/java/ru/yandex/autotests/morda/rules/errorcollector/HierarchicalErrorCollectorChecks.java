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
public class HierarchicalErrorCollectorChecks {
    private static final long DEFAULT_TIMEOUT = 30;
    private final List<List<Runnable>> checks;
    private final List<Throwable> errors;

    public HierarchicalErrorCollectorChecks() {
        checks = new ArrayList<>();
        errors = new ArrayList<>();
    }

    public HierarchicalErrorCollectorChecks run() {
        ExecutorService executorService = Executors.newCachedThreadPool();

        for (List<Runnable> list : checks) {
            final CountDownLatch countDownLatch = new CountDownLatch(list.size());

            list.stream().forEach((runnable) ->
                    executorService.execute(check(runnable, countDownLatch)));

            try {
                countDownLatch.await(DEFAULT_TIMEOUT, TimeUnit.SECONDS);
            } catch (InterruptedException e) {
                throw new RuntimeException("TIMEOUT WAS EXCEEDED", e);
            }
        }

        try {
            executorService.shutdown();
            executorService.awaitTermination(DEFAULT_TIMEOUT, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            throw new RuntimeException("TIMEOUT WAS EXCEEDED", e);
        }

        return this;
    }

    public List<Throwable> getErrors() {
        return this.errors;
    }

    public HierarchicalErrorCollectorChecks check(Runnable... checks) {
        check(asList(checks));
        return this;
    }

    public HierarchicalErrorCollectorChecks check(List<Runnable> checks) {
        if (checks.size() > 0) {
            this.checks.add(checks);
        }
        return this;
    }

    private Runnable check(Runnable runnable, CountDownLatch countDownLatch) {
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
