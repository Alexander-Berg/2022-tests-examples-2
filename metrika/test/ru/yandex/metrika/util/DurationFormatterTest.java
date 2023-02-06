package ru.yandex.metrika.util;

import java.util.Collection;

import org.joda.time.Duration;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.util.locale.LocaleDictionaries;

import static java.util.Arrays.asList;
import static org.assertj.core.api.Assertions.assertThat;
import static org.joda.time.Duration.millis;
import static org.joda.time.Duration.standardDays;
import static org.joda.time.Duration.standardHours;
import static org.joda.time.Duration.standardMinutes;
import static org.joda.time.Duration.standardSeconds;
import static org.mockito.Matchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

@RunWith(Parameterized.class)
public class DurationFormatterTest {

    private static Duration standardWeeks(long weeks) {
        return standardDays(weeks * 7);
    }

    private static Duration duration(long weeks, long days, long hours, long minutes, long seconds, long millis) {
        return standardWeeks(weeks)
                .plus(standardDays(days))
                .plus(standardHours(hours))
                .plus(standardMinutes(minutes))
                .plus(standardSeconds(seconds))
                .plus(millis(millis));
    }

    @Parameterized.Parameters(name = "{1}")
    public static Collection<Object[]> getParameters() {
        return asList(new Object[][] {
                { standardWeeks(1), "1 неделя" },
                { standardWeeks(2), "2 недели" },
                { standardWeeks(5), "5 недель" },

                { standardWeeks(11), "11 недель" },
                { standardWeeks(12), "12 недель" },
                { standardWeeks(15), "15 недель" },

                { standardWeeks(21), "21 неделя" },
                { standardWeeks(22), "22 недели" },
                { standardWeeks(25), "25 недель" },

                { standardWeeks(111), "111 недель" },
                { standardWeeks(112), "112 недель" },
                { standardWeeks(115), "115 недель" },

                { standardDays(1), "1 день" },
                { standardDays(2), "2 дня" },
                { standardDays(5), "5 дней" },

                { standardHours(1), "1 час" },
                { standardHours(2), "2 часа" },
                { standardHours(5), "5 часов" },

                { standardMinutes(1), "1 минута" },
                { standardMinutes(2), "2 минуты" },
                { standardMinutes(5), "5 минут" },

                { standardSeconds(1), "1 секунда" },
                { standardSeconds(2), "2 секунды" },
                { standardSeconds(5), "5 секунд" },

                { standardWeeks(1).plus(standardDays(1)), "1 неделя 1 день" },
                { standardDays(1).plus(standardHours(1)), "1 день 1 час" },
                { standardHours(1).plus(standardMinutes(1)), "1 час 1 минута" },
                { standardMinutes(1).plus(standardSeconds(1)), "1 минута 1 секунда" },

                { duration(1, 0, 1, 1, 1, 1), "1 неделя" },
                { duration(0, 1, 0, 1, 1, 1), "1 день" },
                { duration(0, 0, 1, 0, 1, 1), "1 час" },
                { duration(0, 0, 0, 1, 0, 1), "1 минута" },

                { duration(1, 1, 1, 1, 1, 1), "1 неделя 1 день" },
                { duration(0, 1, 1, 1, 1, 1), "1 день 1 час" },
                { duration(0, 0, 1, 1, 1, 1), "1 час 1 минута" },
                { duration(0, 0, 0, 1, 1, 1), "1 минута 1 секунда" },
                { duration(0, 0, 0, 0, 1, 1), "1 секунда" },
                { duration(0, 0, 0, 0, 0, 1), "0 секунд" },

                { duration(42, 6, 23, 59, 59, 999), "42 недели 6 дней" },
                { duration(0, 6, 23, 59, 59, 999), "6 дней 23 часа" },
                { duration(0, 0, 23, 59, 59, 999), "23 часа 59 минут" },
                { duration(0, 0, 0, 59, 59, 999), "59 минут 59 секунд" },
                { duration(0, 0, 0, 59, 59, 999), "59 минут 59 секунд" },
                { duration(0, 0, 0, 0, 59, 999), "59 секунд" },
                { duration(0, 0, 0, 0, 0, 999), "0 секунд" },

                { millis(0), "0 секунд" },
        });
    }

    @Parameterized.Parameter
    public Duration duration;

    @Parameterized.Parameter(1)
    public String expectedFormattedDuration;

    private DurationFormatter durationFormatter;

    @Before
    public void init() {
        LocaleDictionaries localeDictionaries = mock(LocaleDictionaries.class);
        when(localeDictionaries.keyToLocal(anyString(), anyString()))
                .thenAnswer(invocation -> invocation.getArguments()[1]);

        durationFormatter = new DurationFormatter(localeDictionaries);
        durationFormatter.init();
    }

    @Test
    public void formatDuration() {
        String result = durationFormatter.formatDuration(duration);
        assertThat(result).isEqualTo(expectedFormattedDuration);
    }
}
