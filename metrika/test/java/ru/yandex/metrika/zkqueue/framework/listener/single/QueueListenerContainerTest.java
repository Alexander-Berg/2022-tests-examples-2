package ru.yandex.metrika.zkqueue.framework.listener.single;

import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;

import com.google.common.collect.ImmutableList;
import org.awaitility.Duration;
import org.hamcrest.Matchers;
import org.junit.Test;

import ru.yandex.metrika.zkqueue.core.ZkQueue;
import ru.yandex.metrika.zkqueue.core.curator.CuratorManager;
import ru.yandex.metrika.zkqueue.core.curator.ZkOptions;
import ru.yandex.metrika.zkqueue.core.redelivery.AlwaysConsume;
import ru.yandex.metrika.zkqueue.core.redelivery.ConsumeOnce;
import ru.yandex.metrika.zkqueue.framework.listener.BaseFrameworkTest;

import static com.google.common.util.concurrent.Uninterruptibles.sleepUninterruptibly;
import static org.awaitility.Awaitility.await;
import static org.hamcrest.CoreMatchers.is;
import static ru.yandex.metrika.zkqueue.framework.listener.ListenerTimeoutSettings.defaultSettings;
import static ru.yandex.metrika.zkqueue.framework.listener.ListenerTimeoutSettings.optimisticSettings;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.SYNC_TIME;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.connectionTimeout;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.destination1;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.destination2;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.payload1;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.retryPolicy;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.sessionTimeout;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.syncTime;

public final class QueueListenerContainerTest extends BaseFrameworkTest {

    @Test
    public void checkSimpleProduceAndConsume() throws Exception {
        final AtomicReference<String> content = new AtomicReference<>();
        final ListenerContainer container = new QueueListenerContainer(10, queue, destination1(),
                new ConsumeOnce(), optimisticSettings(), (c, m) -> content.set(m));
        container.start();

        put1(destination1(), payload1());
        await().pollDelay(Duration.ONE_SECOND)
                .atMost(syncTime(), TimeUnit.MILLISECONDS)
                .untilAtomic(content, Matchers.equalTo(payload1()));

        container.stop();
    }

    @Test
    public void checkProduceAndConsumeWhenAllWorkersBusy() throws Exception {
        final AtomicInteger consumed = new AtomicInteger();
        final ListenerContainer container = new QueueListenerContainer(1, queue, destination1(),
                new ConsumeOnce(), optimisticSettings(), (c, m) -> {
            sleepUninterruptibly(1, TimeUnit.SECONDS);
            consumed.incrementAndGet();
        });
        container.start();

        put1(destination1(), payload1());
        put1(destination1(), payload1());
        await().atMost(syncTime(), TimeUnit.MILLISECONDS)
                .untilAtomic(consumed, is(2));

        container.stop();
    }

    @Test
    public void checkDestinationsIsolation() throws Exception {
        final AtomicReference<String> content = new AtomicReference<>();
        final ListenerContainer container = new QueueListenerContainer(10, queue, destination2(),
                new ConsumeOnce(), optimisticSettings(), (c, m) -> content.set(m));
        container.start();

        put1(destination1(), payload1());
        await().pollDelay(Duration.ONE_SECOND)
                .atMost(SYNC_TIME, TimeUnit.MILLISECONDS)
                .untilAtomic(content, Matchers.not(Matchers.equalTo(payload1())));

        container.stop();
    }

    @Test
    public void checkRedelivery() throws Exception {
        final AtomicBoolean consumedByFailedConsumer = new AtomicBoolean();
        final ListenerContainer failingContainer = new QueueListenerContainer(10, queue1, destination1(),
                new AlwaysConsume(), optimisticSettings(), (c, m) -> {
            consumedByFailedConsumer.set(true);
            throw new RuntimeException();
        });

        put1(destination1(), payload1());
        failingContainer.start();

        await().atMost(SYNC_TIME, TimeUnit.MILLISECONDS)
                .untilAtomic(consumedByFailedConsumer, is(true));

        failingContainer.stop();
        queue1.close();

        ZkQueue queue2 = new ZkQueue(new CuratorManager(new ZkOptions(
                server.getConnectString(), sessionTimeout(), connectionTimeout(), retryPolicy())));
        queue2.createIfNeeded(ImmutableList.of(destination1(), destination2()));

        final AtomicReference<String> content = new AtomicReference<>();
        final ListenerContainer container = new QueueListenerContainer(10, queue2, destination1(),
                new AlwaysConsume(), defaultSettings(), (c, m) -> content.set(m));
        container.start();
        await().pollDelay(Duration.ONE_SECOND)
                .atMost(SYNC_TIME, TimeUnit.MILLISECONDS)
                .untilAtomic(content, Matchers.equalTo(payload1()));

        container.stop();
        queue2.close();
    }

    @Test
    public void checkListenerChaining() throws Exception {
        final AtomicReference<String> finalOutput = new AtomicReference<>();

        final QueueListenerContainer listener1 = new QueueListenerContainer(10, queue, destination1(),
                new AlwaysConsume(), optimisticSettings(), (c, m) -> c.putOnCommit(destination2(), m));

        final QueueListenerContainer listener2 = new QueueListenerContainer(10, queue, destination2(),
                new AlwaysConsume(), defaultSettings(), (c, m) -> finalOutput.set(m));

        put1(destination1(), payload1());

        listener1.start();
        listener2.start();

        await().atMost(SYNC_TIME, TimeUnit.MILLISECONDS)
                .untilAtomic(finalOutput, Matchers.equalTo(payload1()));

        listener1.stop();
        listener2.stop();
    }

    @Test
    public void checkBottleneck() throws Exception {
        final int messagesCount = 100;
        final int threadsCount = 2;

        final AtomicInteger consumed = new AtomicInteger();

        final QueueListenerContainer listener = new QueueListenerContainer(threadsCount, queue, destination1(),
                new AlwaysConsume(), optimisticSettings(), (c, m) -> consumed.incrementAndGet());
        listener.start();

        for (int index = 0; index < messagesCount; index++) {
            put1(destination1(), payload1());
        }

        await().atMost(SYNC_TIME, TimeUnit.MILLISECONDS)
                .untilAtomic(consumed, is(messagesCount));

        listener.stop();
    }

    @Test
    public void checkSessionExpirationIsTolerated() throws Exception {
        final AtomicInteger consumed = new AtomicInteger();

        final QueueListenerContainer listener = new QueueListenerContainer(1, queue, destination1(),
                new AlwaysConsume(), optimisticSettings(), (c, m) -> consumed.incrementAndGet());
        listener.start();

        put1(destination1(), payload1());
        await().atMost(SYNC_TIME, TimeUnit.MILLISECONDS)
                .untilAtomic(consumed, is(1));

        expireSession1();

        put1(destination1(), payload1());
        await().atMost(SYNC_TIME, TimeUnit.MILLISECONDS)
                .untilAtomic(consumed, is(2));


        listener.stop();
    }

    @Test
    public void checkConnectionClosingIsTolerated() throws Exception {
        final AtomicInteger consumed = new AtomicInteger();

        final QueueListenerContainer listener = new QueueListenerContainer(1, queue, destination1(),
                new AlwaysConsume(), optimisticSettings(), (c, m) -> consumed.incrementAndGet());
        listener.start();

        put1(destination1(), payload1());
        await().atMost(SYNC_TIME, TimeUnit.MILLISECONDS)
                .untilAtomic(consumed, is(1));

        disconnectClient1();

        put1(destination1(), payload1());
        await().atMost(SYNC_TIME, TimeUnit.MILLISECONDS)
                .untilAtomic(consumed, is(2));


        listener.stop();
    }

    @Test
    public void checkServerFlappingDoesNotCauseProblems() throws Exception {
        final AtomicInteger consumed = new AtomicInteger();

        final QueueListenerContainer listener = new QueueListenerContainer(1, queue, destination1(),
                new AlwaysConsume(), optimisticSettings(), (c, m) -> consumed.incrementAndGet());
        listener.start();

        put1(destination1(), payload1());
        await().atMost(SYNC_TIME, TimeUnit.MILLISECONDS)
                .untilAtomic(consumed, is(1));

        restartServer1();

        await().atMost(SYNC_TIME, TimeUnit.MILLISECONDS)
                .ignoreExceptions()
                .until(() -> {
                    put1(destination1(), payload1());
                    return true;
                });


        await().atMost(SYNC_TIME, TimeUnit.MILLISECONDS)
                .untilAtomic(consumed, is(2));

        listener.stop();
    }


}
