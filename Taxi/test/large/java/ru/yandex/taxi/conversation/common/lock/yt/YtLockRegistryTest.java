package ru.yandex.taxi.conversation.common.lock.yt;

import java.util.UUID;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.context.junit.jupiter.SpringJUnitConfig;

@SpringJUnitConfig(classes = YtLockRegistryTestConfig.class)
@TestPropertySource("classpath:/application.properties")
@Tag("Integration")
public class YtLockRegistryTest {

    @Autowired
    public YtLockRegistryTestConfig.YtLockRegistryFactory lockRegistryFactory;

    /**
     * Работаем с одним экземпляром блокировщика.
     * Получаем лок по ключу.
     * Ожидаем успешное получение лока.
     */
    @Test
    public void tryLock() {

        // arrange
        var lockRegistry = lockRegistryFactory.create();
        var lockKey = "test-" + UUID.randomUUID();

        // act
        var result = 10;
        var lock = lockRegistry.obtain(lockKey);
        if (lock.tryLock()) {
            try {
                result = result * result;
            } finally {
                lock.unlock();
            }
        }

        // assert
        Assertions.assertEquals(100, result);
    }

    /**
     * Работаем с одним экземпляром блокировщика.
     * Берем первый лок на ресурс.
     * Внутри первого лока берем еще один лок на тот же самый ресурс.
     * Ожидаем успешное получение обоих локов.
     */
    @Test
    public void tryLock_withNestedLock() {

        // arrange
        var lockRegistry = lockRegistryFactory.create();
        var lockKey = "test-" + UUID.randomUUID();
        boolean firstLockTaken = false;
        boolean secondLockTaken = false;

        // act
        var lock = lockRegistry.obtain(lockKey);
        if (lock.tryLock()) {
            try {
                firstLockTaken = true;

                if (lock.tryLock()) {
                    try {
                        secondLockTaken = true;
                    } finally {
                        lock.unlock();
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
