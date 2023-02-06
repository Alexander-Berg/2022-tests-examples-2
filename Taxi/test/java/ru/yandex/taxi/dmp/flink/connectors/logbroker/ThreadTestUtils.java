package ru.yandex.taxi.dmp.flink.connectors.logbroker;

import java.util.Objects;
import java.util.Set;
import java.util.concurrent.Callable;

import lombok.experimental.UtilityClass;
import org.apache.flink.core.testutils.CheckedThread;
import org.apache.flink.util.function.ThrowingConsumer;

import static java.lang.Thread.State.TERMINATED;
import static org.junit.Assert.fail;

@UtilityClass
public final class ThreadTestUtils {
    public static void waitNonTerminatedState(Thread thread, Thread.State state) throws InterruptedException {
        while (!Objects.equals(state, thread.getState())) {
            if (thread.getState().equals(TERMINATED)) {
                fail("Terminated before " + state);
            }
            Thread.sleep(10);
        }
    }

    public static void waitNonTerminatedState(Thread thread, Set<Thread.State> states) throws InterruptedException {
        while (!states.contains(thread.getState())) {
            if (thread.getState().equals(TERMINATED)) {
                fail("Terminated before " + states);
            }
            Thread.sleep(10);
        }
    }

    /**
     * У всех тестов, использующих данный метод, должен быть timeout.
     * Иначе они могут зависнуть в бесконечном ожидании.
     */
    public static <T extends BlockedClosable> void testBlockedMethodLifecycle(
            T object,
            ThrowingConsumer<T, Exception> init,
            ThrowingConsumer<T, Exception> blockedMethod,
            ThrowingConsumer<T, Exception> onBlock
    ) throws Exception {
        init.accept(object);
        CheckedThread blockedThread = new CheckedThread() {
            @Override
            public void go() throws Exception {
                blockedMethod.accept(object);
            }
        };

        // должно заблокировать выполнение blockedThread
        object.blockByTest(() -> {
            blockedThread.start();
            // если blockedMethod не синхронизирован/не берет лок, то тест упадет по таймауту
            ThreadTestUtils.waitNonTerminatedState(blockedThread, object.getBlockedThreadState());
            onBlock.accept(object);
            return null;
        });

        // blockedThread должно было разблокировать
        blockedThread.sync();
        if (object.isRunning()) {
            object.close();
        }
    }

    public interface BlockedClosable {
        boolean isRunning();

        void close() throws Exception;

        void blockByTest(Callable<Void> callable) throws Exception;

        Thread.State getBlockedThreadState();
    }
}
