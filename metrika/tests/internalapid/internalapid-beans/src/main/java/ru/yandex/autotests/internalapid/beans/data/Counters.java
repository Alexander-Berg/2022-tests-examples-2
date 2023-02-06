package ru.yandex.autotests.internalapid.beans.data;

import static ru.yandex.autotests.internalapid.beans.data.Counter.ID;

public class Counters {
    public static final Counter SIMPLE_COUNTER = new Counter("Тестовый счетчик обычный")
            .put(ID, 56850799L);
    public static final Counter METRIKA = new Counter("metrika").put(ID, 29761725L);
    public static final Counter COUNTER_WITH_SOURCE = new Counter("Turbo Pages kKVMj")
            .put(ID, 50376028L);
    public static final Counter PINCODE_TEST_COUNTER = new Counter("SV").put(ID, 65713078L);
}
