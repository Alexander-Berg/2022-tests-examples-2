package ru.yandex.autotests.metrika.data.common;

import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.counters.Counters;

import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_COUNTER_LIMITS;

/**
 * Created by konkov on 14.08.2015.
 */
public final class CounterConstants {

    /**
     * Счетчик для тестов, которые не нужндаются в данных
     */
    public static final Counter NO_DATA = TEST_COUNTER_LIMITS;

    /**
     * Счетчик для тестов, которые нужндаются в небольшом количестве данных
     */
    public static final Counter LITE_DATA = Counters.SENDFLOWERS_RU;

    /**
     * счетчик для тестов, которые не нуждаются в данных, но которым требуется direct_client_ids
     */
    public static final Counter NO_DATA_WITH_CLICKS = Counters.SENDFLOWERS_RU;

    /**
     * Счетчик для тестов с публичным доступом
     */
    public static final Counter PUBLIC_COUNTER = Counters.FEELEK;

}
