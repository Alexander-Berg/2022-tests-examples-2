package ru.yandex.taxi.conversation.common.lock.yt;

import java.util.UUID;
import java.util.concurrent.Semaphore;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.context.junit.jupiter.SpringJUnitConfig;

@SpringJUnitConfig(classes = YtLockRegistryTestConfig.class)
@TestPropertySource("classpath:/application.properties")
@Tag("Integration")
public class YtLockRegistryTwoInstancesTest {

    @Autowired
    public YtLockRegistryTestConfig.YtLockRegistryFactory lockRegistryFactory;

    /**
     * Работаем с двумя инстансами блокировщика имитируя две ноды приложения.
     * Первым инстансом берем лок по ключу. Затем пока ключ занят пытаемся взять вторым инстансом лок на тот же самый
     * ключ
     * с указанием времени ожидания взятия лока.
     * Ожидаем успешное получение лока.
     */
    @Test
    public void twoInstances_tryLock_withParams() throws InterruptedException {
        // arrange
        var lockRegistry1 = lockRegistryFactory.create();
        var lockRegistry2 = lockRegistryFactory.create();

        var lockKey = "test-" + UUID.randomUUID();
        AtomicBoolean firstLockReleased = new AtomicBoolean(false);
        AtomicBoolean secondLockTaken = new AtomicBoolean(false);
        var start = new Semaphore(1);

        var t1 = new Thread(() -> {
            try {
                start.acquire();
                var lock = lockRegistry1.obtain(lockKey);
                if (lock.tryLock()) {
                    try {
                        Thread.sleep(200);
                    } finally {
                        lock.unlock();
                        firstLockReleased.set(true);
                        start.release();
                    }
                }
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        });

        var t2 = new Thread(() -> {
            try {
                start.acquire();
                var lock = lockRegistry2.obtain(lockKey);
                if (lock.tryLock(500, TimeUnit.MILLISECONDS)) {
                    try {
                        secondLockTaken.set(true);
                    } finally {
                        lock.unlock();
                    }
                }
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        });

        // act
        t1.start();
        t2.start();
        t2.join();

        // assert
        Assertions.assertTrue(firstLockReleased.get());
        Assertions.assertTrue(secondLockTaken.get());
    }

    /**
     * Работаем с двумя инстансами блокировщика имитируя две ноды приложения.
     * Первым инстансом берем лок а затем вторым пытаемся взять лок на тот же самый ресурс.
     * Ожидаем, что пока ресурс занят первым приложением второе приложение взять лок на него не сможет.
     */
    @Test()
    public void twoInstances_shouldTakeOnlyOneLock_onTheSameResource() {

        // arrange
        var lockRegistry1 = lockRegistryFactory.create();
        boolean firstLockTaken = false;

        var lockRegistry2 = lockRegistryFactory.create();
        boolean secondLockTaken = false;

        var lockKey = "test-" + UUID.randomUUID();

        // act
        var lock = lockRegistry1.obtain(lockKey);
        if (lock.tryLock()) {
            try {
                firstLockTaken = true;

                var lock2 = lockRegistry2.obtain(lockKey);
                if (lock2.tryLock()) {
                    try {
                        secondLockTaken = true;
                    } finally {
                        lock2.unlock();
                    }
                }

            } finally {
                lock.unlock();
            }
        }

        // assert
        Assertions.assertTrue(firstLockTaken);
        Assertions.assertFalse(secondLockTaken);
    }

    /**
     * Работаем с двумя инстансами блокировщика имитируя две ноды приложения.
     * Первым инстансом берем лок а затем вторым пытаемся взять лок на другой ресурс.
     * Ожидаем, что пока первый ресурс занят первым приложением второе приложение может взять лок на другой ресурс.
     */
    @Test()
    public void twoInstances_shouldTakeLocks_onDifferentResources() {

        // arrange
        var lockRegistry1 = lockRegistryFactory.create();
        var firstLockKey = "test-" + UUID.randomUUID();
        boolean firstLockTaken = false;

        var lockRegistry2 = lockRegistryFactory.create();
        var secondLockKey = "test-" + UUID.randomUUID();
        boolean secondLockTaken = false;

        // act
        var lock = lockRegistry1.obtain(firstLockKey);
        if (lock.tryLock()) {
            try {
                firstLockTaken = true;

                var lock2 = lockRegistry2.obtain(secondLockKey);
                if (lock2.tryLock()) {
                    try {
                        secondLockTaken = true;
                    } finally {
                        lock2.unlock();
                    }
                }

            } finally {
                lock.unlock();
            }
        }

        // assert
        Assertions.assertTrue(firstLockTaken);
        Assertions.assertTrue(secondLockTaken);
    }
}
