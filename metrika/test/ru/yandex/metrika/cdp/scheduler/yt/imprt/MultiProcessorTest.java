package ru.yandex.metrika.cdp.scheduler.yt.imprt;

import java.time.Duration;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.stream.Stream;

import org.awaitility.Awaitility;
import org.awaitility.core.ThrowingRunnable;
import org.jetbrains.annotations.NotNull;
import org.junit.Assert;
import org.junit.Test;
import org.mockito.Mockito;
import org.mockito.invocation.InvocationOnMock;
import org.mockito.stubbing.Answer;

/**
 * Тесты {@link MultiProcessor}.
 * <p>
 * {@link CompletableFuture} для {@link MultiProcessor} получаются с помощью класса
 * {@link CompletableFutureAnswerProvider}, который по переданному аргументу достаёт из {@link Map} действие
 * и запускает его с помощью {@link CompletableFuture#runAsync(Runnable)}. При этом исключение,
 * произошедшее внутри действия, упаковывается в {@link RuntimeException}.
 */
public class MultiProcessorTest {

    @SuppressWarnings("unchecked")
    @NotNull
    private final MultiProcessor.StatelessProcessor<Integer> processorMock =
            Mockito.mock(MultiProcessor.StatelessProcessor.class);

    @Test(timeout = 1000L)
    public void oneTask() {
        mockProcessorAnswer(Map.of(
                5, () -> {}
        ));
        try (MultiProcessor<Integer> multiProcessor =
                     new MultiProcessor<>(1, Duration.ofMillis(10L), processorMock)) {
            multiProcessor.accept(5);
        }
        assertProcessorCalls(1);
    }

    private void mockProcessorAnswer(@NotNull Map<Integer, ? extends ThrowingRunnable> answerMap) {
        Mockito
                .when(processorMock.processAsync(Mockito.any()))
                .thenAnswer(new CompletableFutureAnswerProvider(answerMap));
    }

    /**
     * Вспомогательный класс для запуска асинхронных действий при обращении к подставному объекту.
     * Действия берутся по аргументу вызова из переданного в конструктор отображения.
     */
    private static class CompletableFutureAnswerProvider implements Answer<CompletableFuture<Void>> {

        @NotNull
        private final Map<Integer, ? extends ThrowingRunnable> answerMap;

        private CompletableFutureAnswerProvider(@NotNull Map<Integer, ? extends ThrowingRunnable> answerMap) {
            this.answerMap = answerMap;
        }

        @Override
        public CompletableFuture<Void> answer(InvocationOnMock invocation) {
            return CompletableFuture.runAsync(() -> {
                try {
                    answerMap
                            .get(invocation.getArgument(0, Integer.class))
                            .run();
                } catch (Throwable t) {
                    throw new RuntimeException(t);
                }
            });
        }

    }

    private void assertProcessorCalls(int expectedCallCount) {
        Mockito
                .verify(processorMock, Mockito.times(expectedCallCount))
                .processAsync(Mockito.anyInt());
    }

    @Test(timeout = 5000L)
    public void excessiveTaskIsBlocked() throws InterruptedException {
        Map<Integer, ThreadCheckingLatchWaiter> answerMap = Map.of(
                1, new ThreadCheckingLatchWaiter(),
                2, new ThreadCheckingLatchWaiter(),
                3, new ThreadCheckingLatchWaiter()
        );
        mockProcessorAnswer(answerMap);
        try (MultiProcessor<Integer> multiProcessor =
                     new MultiProcessor<>(2, Duration.ofMinutes(1L), processorMock)) {
            // Запустить две заблокированные задачи (максимальное количество параллельно выполняющихся).
            multiProcessor.accept(1);
            multiProcessor.accept(2);
            /*
            Запустить третью задачу в другом потоке, так как метод запуска должен заблокироваться
            до завершения одной из двух первых задач.
             */
            ActingThreadChecker thirdStarter = new ActingThreadChecker(() -> multiProcessor.accept(3));
            runThrowingAsync(thirdStarter);
            // Дождаться запуска первых двух задач и задачи постановки третьей задачи.
            answerMap.get(1).waitForExecutionStarted();
            answerMap.get(2).waitForExecutionStarted();
            thirdStarter.waitForExecutionStarted();
            // Проверить состояние потоков, выполняющих задачи.
            answerMap.get(1).assertExecutingThreadState(Thread.State.WAITING);
            answerMap.get(2).assertExecutingThreadState(Thread.State.WAITING);
            answerMap.get(3).assertExecutionNotStarted();
            thirdStarter.assertExecutingThreadState(Thread.State.TIMED_WAITING);
            // Позволить завершиться второй задаче.
            answerMap.get(2).allowCompletion();
            // Дождаться запуска третьей задачи.
            answerMap.get(3).waitForExecutionStarted();
            // Проверить состояние потоков, выполняющих задачи.
            answerMap.get(1).assertExecutingThreadState(Thread.State.WAITING);
            answerMap.get(3).assertExecutingThreadState(Thread.State.WAITING);
            // Позволить завершиться всем задачам.
            answerMap.get(1).allowCompletion();
            answerMap.get(3).allowCompletion();
        }
        assertProcessorCalls(3);
    }

    /**
     * Расширение {@link ThreadChecker}, блокирующее исполняющий поток до вызова {@link #allowCompletion()}.
     */
    private static class ThreadCheckingLatchWaiter extends ThreadChecker {

        @NotNull
        private final CountDownLatch finishLatch = new CountDownLatch(1);

        @Override
        public void run() throws Throwable {
            super.run();
            finishLatch.await();
        }

        void allowCompletion() {
            finishLatch.countDown();
        }

    }

    /**
     * Расширение {@link ThreadChecker}, выполняющее заданное в конструкторе действие.
     */
    private static class ActingThreadChecker extends ThreadChecker {

        @NotNull
        private final ThrowingRunnable action;

        private ActingThreadChecker(@NotNull ThrowingRunnable action) {
            this.action = action;
        }

        @Override
        public void run() throws Throwable {
            super.run();
            action.run();
        }

    }

    /**
     * Класс {@link ThrowingRunnable}, позволяющий дождаться начала исполнения и проверить состояние исполняющего потока.
     */
    private static class ThreadChecker implements ThrowingRunnable {

        @NotNull
        private final CountDownLatch startLatch = new CountDownLatch(1);

        private volatile Thread taskThread;

        @Override
        public void run() throws Throwable {
            taskThread = Thread.currentThread();
            startLatch.countDown();
        }

        void waitForExecutionStarted() throws InterruptedException {
            startLatch.await();
        }

        void assertExecutionNotStarted() {
            Assert.assertEquals(1, startLatch.getCount());
        }

        void assertExecutingThreadState(@NotNull Thread.State expectedThreadState) {
            Awaitility
                    .waitAtMost(org.awaitility.Duration.FIVE_HUNDRED_MILLISECONDS)
                    .untilAsserted(() -> Assert.assertEquals(expectedThreadState, taskThread.getState()));
        }

    }

    @NotNull
    private CompletableFuture<Void> runThrowingAsync(@NotNull ThrowingRunnable throwingRunnable) {
        return CompletableFuture.runAsync(() -> {
            try {
                throwingRunnable.run();
            } catch (Throwable ignored) {
            }
        });
    }

    @Test(timeout = 5000L)
    public void completionIsBlockedByRunningTasks() throws InterruptedException, TimeoutException, ExecutionException {
        Map<Integer, ThreadCheckingLatchWaiter> answerMap = Map.of(
                1, new ThreadCheckingLatchWaiter(),
                2, new ThreadCheckingLatchWaiter()
        );
        mockProcessorAnswer(answerMap);
        MultiProcessor<Integer> multiProcessor =
                new MultiProcessor<>(2, Duration.ofMinutes(1L), processorMock);
        // Запустить две заблокированные задачи (максимальное количество параллельно выполняющихся).
        multiProcessor.accept(1);
        multiProcessor.accept(2);
        // Запустить завершение в другом потоке, так как метод должен заблокироваться до завершения всех задач.
        ActingThreadChecker completionStarter = new ActingThreadChecker(multiProcessor::close);
        CompletableFuture<Void> completionFuture = runThrowingAsync(completionStarter);
        completionStarter.waitForExecutionStarted();
        completionStarter.assertExecutingThreadState(Thread.State.WAITING);
        // Позволить завершиться первой задаче.
        answerMap.get(1).allowCompletion();
        // Проверить состояние потока завершения.
        completionStarter.assertExecutingThreadState(Thread.State.WAITING);
        // Позволить завершиться оставшейся задаче.
        answerMap.get(2).allowCompletion();
        // Проверить, что ожидание завершения всех задач оказывается недолгим.
        completionFuture.get(100L, TimeUnit.MILLISECONDS);
        assertProcessorCalls(2);
    }

    @Test(timeout = 1000L, expected = RuntimeException.class)
    public void completeThrowsOnSingleException() {
        Map<Integer, ActingThreadChecker> answerMap = Map.of(
                1, new ActingThreadChecker(() -> {}),
                2, new ActingThreadChecker(() -> { throw new IllegalStateException(); }),
                3, new ActingThreadChecker(() -> {})
        );
        mockProcessorAnswer(answerMap);
        MultiProcessor<Integer> multiProcessor =
                new MultiProcessor<>(2, Duration.ofMinutes(1L), processorMock);
        // Запустить все задачи.
        answerMap.keySet().forEach(multiProcessor);
        multiProcessor.close(); // Здесь должно произойти исключение.
        Assert.fail();
    }

    @Test(timeout = 1000L, expected = RuntimeException.class)
    public void completeThrowsOnMultipleException() {
        Map<Integer, ActingThreadChecker> answerMap = Map.of(
                1, new ActingThreadChecker(() -> { throw new IllegalStateException(); }),
                2, new ActingThreadChecker(() -> { throw new IllegalStateException(); }),
                3, new ActingThreadChecker(() -> { throw new IllegalStateException(); })
        );
        mockProcessorAnswer(answerMap);
        MultiProcessor<Integer> multiProcessor =
                new MultiProcessor<>(2, Duration.ofMinutes(1L), processorMock);
        // Запустить все задачи.
        answerMap.keySet().forEach(multiProcessor);
        multiProcessor.close(); // Здесь должно произойти исключение.
        Assert.fail();
    }

    @Test(timeout = 2000L)
    public void previousTasksExceptionDoesNotBreakCurrentCompletion() {
        Map<Integer, ActingThreadChecker> answerMap = Map.of(
                1, new ActingThreadChecker(() -> {}),
                2, new ActingThreadChecker(() -> {}),
                3, new ActingThreadChecker(() -> { throw new IllegalStateException(); }),
                11, new ActingThreadChecker(() -> {}),
                12, new ActingThreadChecker(() -> {}),
                13, new ActingThreadChecker(() -> {})
        );
        mockProcessorAnswer(answerMap);
        try (MultiProcessor<Integer> multiProcessor =
                     new MultiProcessor<>(2, Duration.ofMinutes(1L), processorMock)) {
            // Запустить первую группу задач.
            Set.of(1, 2, 3).forEach(multiProcessor);
            try {
                multiProcessor.close(); // Здесь должно произойти исключение.
                Assert.fail();
            } catch (RuntimeException ignored) {
            }
            // Запустить вторую группу задач.
            Set.of(11, 12, 13).forEach(multiProcessor);
        } // Здесь должно произойти удачное завершение.
        assertProcessorCalls(6);
    }

    @Test(timeout = 1000L)
    public void taskExceptionsDelivered() {
        IllegalStateException firstTaskException = new IllegalStateException();
        IllegalStateException thirdTaskException = new IllegalStateException();
        Map<Integer, ActingThreadChecker> answerMap = Map.of(
                1, new ActingThreadChecker(() -> { throw firstTaskException; }),
                2, new ActingThreadChecker(() -> {}),
                3, new ActingThreadChecker(() -> { throw thirdTaskException; })
        );
        mockProcessorAnswer(answerMap);
        try {
            MultiProcessor<Integer> multiProcessor =
                    new MultiProcessor<>(2, Duration.ofMinutes(1L), processorMock);
            // Запустить все задачи.
            answerMap.keySet().forEach(multiProcessor);
            multiProcessor.close(); // Здесь должно произойти исключение.
            Assert.fail();
        } catch (RuntimeException multiProcessorKitException) {
            Set<Throwable> expectedExceptionSet = Set.of(firstTaskException, thirdTaskException);
            // Исключения задач упакованы в RuntimeException в CompletableFutureAnswerProvider.
            boolean allExceptionsDelivered = Stream
                    .of(multiProcessorKitException.getSuppressed())
                    .map(Throwable::getCause)
                    .allMatch(expectedExceptionSet::contains);
            Assert.assertTrue(allExceptionsDelivered);
        }
    }

    @Test(timeout = 1000L, expected = RuntimeException.class)
    public void waitTimeoutThrew() {
        Map<Integer, ThreadCheckingLatchWaiter> answerMap = Map.of(
                1, new ThreadCheckingLatchWaiter(),
                2, new ThreadCheckingLatchWaiter()
        );
        mockProcessorAnswer(answerMap);
        try (MultiProcessor<Integer> multiProcessor =
                     new MultiProcessor<>(1, Duration.ofMillis(200L), processorMock)) {
            try {
                multiProcessor.accept(1);
                multiProcessor.accept(2); // Этот вызов должен заблокироваться и выдать исключение через 200 мс.
                Assert.fail();
            } finally {
                answerMap.get(1).allowCompletion();
                answerMap.get(2).allowCompletion();
            }
        }
    }

}
