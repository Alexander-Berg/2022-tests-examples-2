package ru.yandex.metrika.processing.ratelimit;

import java.time.Clock;
import java.util.List;

import com.vividsolutions.jts.util.Assert;
import org.junit.Before;
import org.junit.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.MockitoAnnotations;

import ru.yandex.metrika.util.collections.F;

/**
 * Мокаем функцию millis() и проверяем, что алгоритм лимитирует RPS.
 */
public class TokenBucketAlgorithmTest {

    /**
     * Произвольный ключ бакета. Всегда тестируем только один бакет и не проверяем concurrency.
     */
    private static final int KEY = 1;
    /**
     * Пусть токен добавляется в бакет каждые 10 мс
     */
    private static final int RPS = 100;

    @Mock
    private Clock clock;

    @InjectMocks
    private TokenBucketAlgorithm<Integer> tokenBucketAlgorithm;

    @Before
    public void setup() {
        MockitoAnnotations.initMocks(this);
    }

    @Test
    public void check() {
        List<Integer> tokens = acquireTokens(new Long[]{1000L, 1300L, 1500L, 2000L, 3000L});
        Assert.equals(List.of(100, 30, 20, 50, 100), tokens);
    }

    @Test
    public void checkEscalation() {
        List<Integer> tokens = acquireTokens(new Long[]{100L, 1000L});
        Assert.equals(List.of(100, 90), tokens);
    }

    @Test
    public void checkTwoSeconds() {
        List<Integer> tokens = acquireTokens(new Long[]{1000L, 2000L, 4000L, 4010L});
        Assert.equals(List.of(100, 100, 100, 1), tokens);
    }

    @Test
    public void checkZero() {
        List<Integer> tokens = acquireTokens(new Long[]{1000L, 1005L, 1010L, 2000L});
        Assert.equals(List.of(100, 0, 1, 99), tokens);
    }

    /**
     * Вызов hasFreeTokens тоже перенаполняет бакет, проверим и это место.
     */
    @Test
    public void checkHasFreeTokens() {
        Mockito.when(clock.millis()).thenReturn(0L, 1000L, 1005L, 1200L, 1300L);

        Assert.equals(tokenBucketAlgorithm.acquireTokens(KEY, RPS, RPS, RPS), 100);
        Assert.isTrue(!tokenBucketAlgorithm.hasFreeTokens(KEY, RPS, RPS));
        Assert.isTrue(tokenBucketAlgorithm.hasFreeTokens(KEY, RPS, RPS));
        Assert.equals(tokenBucketAlgorithm.acquireTokens(KEY, RPS, RPS, RPS), 30);
    }

    private List<Integer> acquireTokens(Long[] timePoints) {
        Mockito.when(clock.millis()).thenReturn(0L, timePoints);
        return F.map(timePoints, tp -> tokenBucketAlgorithm.acquireTokens(KEY, RPS, RPS, RPS));
    }
}
