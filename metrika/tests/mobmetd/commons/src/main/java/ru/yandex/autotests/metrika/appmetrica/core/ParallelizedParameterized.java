package ru.yandex.autotests.metrika.appmetrica.core;

import org.junit.runners.Parameterized;
import org.junit.runners.model.RunnerScheduler;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;

import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;

public class ParallelizedParameterized extends Parameterized {

    public ParallelizedParameterized(Class clazz) throws Throwable {
        super(clazz);
        setScheduler(new ThreadPoolScheduler());
    }

    private static class ThreadPoolScheduler implements RunnerScheduler {

        private static final AtomicLong threadsCounter = new AtomicLong();

        private final ExecutorService executor = Executors.newFixedThreadPool(
                apiProperties().getParallelParametersThreads(),
                runnable -> new Thread(runnable, "params-" + threadsCounter.incrementAndGet()));

        @Override
        public void finished() {
            executor.shutdown();
            try {
                // Общий таймаут сразу на все тест-кейзы.
                // Если тесты не успеют выполниться, то в отчёт Allure попадёт тест-кейз с названием Test was interrupted,
                // а иногда отчёт вовсе не построится из-за бага с асинхронностью в AllureShutdownHook (Allure 1.5)
                executor.awaitTermination(3, TimeUnit.HOURS);
            } catch (InterruptedException exc) {
                throw new RuntimeException(exc);
            }
        }

        @Override
        public void schedule(Runnable childStatement) {
            executor.submit(childStatement);
        }
    }

}
