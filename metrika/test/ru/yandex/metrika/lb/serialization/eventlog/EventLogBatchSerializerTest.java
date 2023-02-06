package ru.yandex.metrika.lb.serialization.eventlog;

import java.util.Collection;
import java.util.List;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.lb.serialization.proto.GenericProtoSerializer;
import ru.yandex.metrika.lb.ut.TestEvents.TOneOf;
import ru.yandex.metrika.util.io.IOUtils;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static ru.yandex.metrika.lb.ut.TestEvents.TOneField;
import static ru.yandex.metrika.lb.ut.TestEvents.TTwoFields;

/**
 * @see <a href="https://a.yandex-team.ru/arc_vcs/junk/lavrinovich/cpp/event_log_v5_gen">junk/lavrinovich/cpp/event_log_v5_gen</a>
 * Это утилита используется для генерации файликов, лежащих в папочке data
 */
@RunWith(Parameterized.class)
public class EventLogBatchSerializerTest {
    private static final int EXPECTED_FRAME_COUNT = 10;
    private static final EventLogBatchSerializer<TOneOf> PARSER = new EventLogBatchSerializer<>(
            new GenericProtoSerializer<>(TOneOf.parser())
    );

    @Parameterized.Parameter
    public String file;

    @Parameterized.Parameters(name = "file: {0}")
    public static Collection<Object[]> createParameters() {
        return List.of(
                new Object[]{"data/eventlog_v4.data"},
                new Object[]{"data/eventlog_v5.data"},
                new Object[]{"data/eventlog_default.data"}
        );
    }

    @Test
    public void testParse() {
        var bytes = IOUtils.resourceAsBytes(getClass(), file);
        var events = List.copyOf(PARSER.deserialize(bytes));
        assertEquals(EXPECTED_FRAME_COUNT * (EXPECTED_FRAME_COUNT + 1) / 2, events.size());
        int realIndex = 0;
        for (int i = 0; i < 10; ++i) {
            var str = Integer.toString(i);
            for (int j = 0; j <= i; ++j) {
                TOneOf oneOf = events.get(realIndex);
                if (j % 2 == 1) {
                    assertTrue(oneOf.hasFirst());
                    assertEquals(
                            TOneField.newBuilder().setStr1(str).build(),
                            oneOf.getFirst()
                    );
                } else {
                    assertTrue(oneOf.hasSecond());
                    assertEquals(
                            TTwoFields.newBuilder().setStr1(str).setStr2(str).build(),
                            oneOf.getSecond()
                    );
                }
                ++realIndex;
            }
        }
    }
}
