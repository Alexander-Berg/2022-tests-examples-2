package ru.yandex.autotests.advapi.threading;

import java.util.concurrent.ThreadFactory;
import java.util.concurrent.atomic.AtomicInteger;

import static java.lang.String.format;

/**
 * Created by konkov on 21.03.2016.
 */
public class CustomThreadFactory implements ThreadFactory {
    private final AtomicInteger id = new AtomicInteger();
    private final String name;
    private final boolean isDaemon;

    public CustomThreadFactory(String name, boolean isDaemon) {
        this.name = name;
        this.isDaemon = isDaemon;
    }

    @Override
    public Thread newThread(Runnable r) {
        Thread thread = new Thread(r, format("%s-%d", name, id.getAndIncrement()));
        thread.setDaemon(isDaemon);
        return thread;
    }
}
