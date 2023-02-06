package ru.yandex.metrika.test;


import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;

import javax.annotation.Nonnull;

/**
 * Реализация стандартных часов в Java для тестов
 * Пример использования:
 * void test() {
 *     var mc = new ManualClock();
 *     var obj = new TimeDependentObj(mc);
 *     obj.doSomeWork();
 *     mc.tick(Duration.ofMinutes(1));
 *     obj.doSomeWork();
 *     assert obj.check();
 * }
 *
 * @see java.time.Clock
 */
public class ManualClock extends Clock {

    @Nonnull
    private Clock delegate;

    public ManualClock() {
        this(Instant.EPOCH);
    }

    public ManualClock(Instant now) {
        delegate = Clock.fixed(now, ZoneOffset.UTC);
    }

    private ManualClock(@Nonnull Clock delegate) {
        this.delegate = delegate;
    }

    public void offset(Duration duration) {
        delegate = Clock.offset(delegate, duration);
    }

    @Override
    public ZoneId getZone() {
        return delegate.getZone();
    }

    @Override
    public ManualClock withZone(ZoneId zone) {
        return new ManualClock(delegate.withZone(zone));
    }

    @Override
    public Instant instant() {
        return delegate.instant();
    }
}
