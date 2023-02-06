package ru.yandex.autotests.metrika.utils;

import java.util.concurrent.Callable;

import com.google.common.base.Throwables;

import static com.google.common.base.Preconditions.checkArgument;

public class Try {

    public static void retry(Runnable f, int c, long sleepTimeMs, double multiplier) {
        try {
            new Retry<>(() -> {
                f.run();
                return null;
            }, c, sleepTimeMs, multiplier).call();
        } catch (Exception e) {
            throw Throwables.propagate(e);
        }
    }

    static class Retry<T> implements Callable<T> {
        private final Callable<T> delegate;
        private final int count;
        private final long sleepTimeMs;
        private final double multiplier;

        Retry(Callable<T> delegate, int count, long sleepTimeMs, double multiplier) {
            checkArgument(count > 0, "nonpositive count %s", count);
            this.delegate = delegate;
            this.count = count;
            this.sleepTimeMs = sleepTimeMs;
            this.multiplier = multiplier;
        }

        @Override
        public T call() throws Exception {
            long calculatedSleepTimeMs = sleepTimeMs;
            Exception ee = null;
            for (int i = 0; i < count; i++) {
                if ((sleepTimeMs > 0) && (i > 0)) {
                    calculatedSleepTimeMs = (long) ((double) calculatedSleepTimeMs * multiplier);
                    try {
                        Thread.sleep(calculatedSleepTimeMs);
                    } catch (InterruptedException r) {
                        Thread.currentThread().interrupt();
                        throw r;
                    }
                }
                try {
                    return delegate.call();
                } catch (Exception e) {
                    if (ee == null) {
                        ee = e;
                    } else {
                        ee.addSuppressed(e);
                    }
                }
            }
            throw ee;
        }

    }
}
