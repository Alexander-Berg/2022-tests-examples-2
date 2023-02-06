package ru.yandex.metrika.util.time;

import java.util.Collection;

import com.google.common.collect.ImmutableList;
import junit.framework.TestCase;
import org.joda.time.DateTime;
import org.joda.time.DateTimeConstants;
import org.joda.time.LocalDate;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;


@RunWith(Parameterized.class)
public class TimeRangesTest extends TestCase {


    static class WeekDays {
        public static final DateTime MONDAY = LocalDate.now().withDayOfWeek(DateTimeConstants.MONDAY).toDateTimeAtStartOfDay();
        public static final DateTime TUESDAY = LocalDate.now().withDayOfWeek(DateTimeConstants.TUESDAY).toDateTimeAtStartOfDay();
        public static final DateTime WEDNESDAY = LocalDate.now().withDayOfWeek(DateTimeConstants.WEDNESDAY).toDateTimeAtStartOfDay();
        public static final DateTime THURSDAY = LocalDate.now().withDayOfWeek(DateTimeConstants.THURSDAY).toDateTimeAtStartOfDay();
        public static final DateTime FRIDAY = LocalDate.now().withDayOfWeek(DateTimeConstants.FRIDAY).toDateTimeAtStartOfDay();
        public static final DateTime SATURDAY = LocalDate.now().withDayOfWeek(DateTimeConstants.SATURDAY).toDateTimeAtStartOfDay();
        public static final DateTime SUNDAY = LocalDate.now().withDayOfWeek(DateTimeConstants.SUNDAY).toDateTimeAtStartOfDay();

    }

    static class Ranges {
        public static final String MONOTONIC = "9-20;9-20;9-20;9-20;9-20;9-20;9-20";
        public static final String WORK_DAYS = "9-20;9-20;9-20;9-20;9-20;;";
        public static final String CROSS_DAY = "0-3,12-23;0-3,12-23;0-3,12-23;0-3,12-23;0-3,12-23;0-3,12-23;0-3,12-23";
        public static final String SMALL_INTERVAL = "10,12,18-19;10,12,18-19;10,12,18-19;10,12,18-19;10,12,18-19;10,12,18-19;10,12,18-19";
        public static final String WITH_ERRORS = "9-20;9-2a;9-20;12b;9-20;9-20;9-20";
        public static final String MONDAY_MORNING = "0;;;;;;";

    }

    @Parameterized.Parameter
    public String description;
    @Parameterized.Parameter(1)
    public String input;
    @Parameterized.Parameter(2)
    public DateTime checkTime;
    @Parameterized.Parameter(3)
    public DateTime expectedNextTime;
    @Parameterized.Parameter(4)
    public boolean isEmpty;
    @Parameterized.Parameter(5)
    public String expectedOutput;


    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                // Монотонный набор одиночных отрезков на всю неделю
                .add(param("Mono-PreRange", Ranges.MONOTONIC,
                        WeekDays.MONDAY, WeekDays.MONDAY.plusHours(9), false))
                .add(param("Mono-InRange", Ranges.MONOTONIC,
                        WeekDays.THURSDAY.plusHours(12), WeekDays.THURSDAY.plusHours(12), false))
                .add(param("Mono-AfterRange", Ranges.MONOTONIC,
                        WeekDays.FRIDAY.plusHours(21), WeekDays.SATURDAY.plusHours(9), false))

                // Набор одиночных отрезков без выходных
                .add(param("WorkDays-InRange", Ranges.WORK_DAYS,
                        WeekDays.FRIDAY.plusHours(12), WeekDays.FRIDAY.plusHours(12), false))
                .add(param("WorkDays-AfterRange-in24h", Ranges.WORK_DAYS,
                        WeekDays.SUNDAY.plusHours(21), WeekDays.MONDAY.plusWeeks(1).plusHours(9), false))
                .add(param("WorkDays-AfterRange-out24h", Ranges.WORK_DAYS,
                        WeekDays.FRIDAY.plusHours(21), null, false))
                // Изменено на новый вариант работы, но для обратной совместимости оставлен поиск только в ближайшем дне
                // В случае перехода на поиск по всей неделе результат будет: WeekDays.MONDAY.plusWeeks(1).plusHours(9)

                // Набор с пересечением даты
                .add(param("CrossDay-InRange-Morning", Ranges.CROSS_DAY,
                        WeekDays.SUNDAY.plusHours(2), WeekDays.SUNDAY.plusHours(2), false))
                .add(param("CrossDay-InRange-Evening", Ranges.CROSS_DAY,
                        WeekDays.SUNDAY.plusHours(22), WeekDays.SUNDAY.plusHours(22), false))
                .add(param("CrossDay-OutRange", Ranges.CROSS_DAY,
                        WeekDays.SUNDAY.plusHours(10), WeekDays.SUNDAY.plusHours(12), false))

                // Набор с маленькими интервалами
                .add(param("SmallInterv-InRange", Ranges.SMALL_INTERVAL,
                        WeekDays.SUNDAY.plusHours(10), WeekDays.SUNDAY.plusHours(10), false))
                .add(param("SmallInterv-Between", Ranges.SMALL_INTERVAL,
                        WeekDays.SUNDAY.plusHours(11), WeekDays.SUNDAY.plusHours(12), false))
                .add(param("SmallInterv-InRange-Noon", Ranges.SMALL_INTERVAL,
                        WeekDays.SUNDAY.plusHours(12), WeekDays.SUNDAY.plusHours(12), false))
                .add(param("SmallInterv-Between-AfterNoon", Ranges.SMALL_INTERVAL,
                        WeekDays.SUNDAY.plusHours(13), WeekDays.SUNDAY.plusHours(18), false))
                .add(param("SmallInterv-inRange-Evening", Ranges.SMALL_INTERVAL,
                        WeekDays.SUNDAY.plusHours(18), WeekDays.SUNDAY.plusHours(18), false))
                .add(param("SmallInterv-Between-CrossWeek", Ranges.SMALL_INTERVAL,
                        WeekDays.SUNDAY.plusHours(20), WeekDays.MONDAY.plusWeeks(1).plusHours(10), false))

                // С пропущенными из-за ошибок интервалами
                .add(param("WithError-InRange-RangeError", Ranges.WITH_ERRORS,
                        WeekDays.TUESDAY.plusHours(12), WeekDays.WEDNESDAY.plusHours(9), false,
                        "9-20;;9-20;;9-20;9-20;9-20"
                ))
                .add(param("WithError-InRange-ValueError", Ranges.WITH_ERRORS,
                        WeekDays.THURSDAY.plusHours(12), WeekDays.FRIDAY.plusHours(9), false,
                        "9-20;;9-20;;9-20;9-20;9-20"
                ))

                // Набор с отправкой только в понедельник ночью (Для проверки интервалов больше одного дня)
                .add(param("MonMon-InRange", Ranges.MONDAY_MORNING,
                        WeekDays.MONDAY, WeekDays.MONDAY, false))

                // Пустой набор
                .add(param("Empty", "",
                        WeekDays.MONDAY, null, true))
                .add(param("FullError", "ERROR RANGE",
                        WeekDays.THURSDAY, null, true,
                        ""
                ))
                .build();
    }

    private static Object[] param(String description, String input, DateTime checkTime, DateTime expectedNextTime, boolean isEmpty) {
        return param(description, input, checkTime, expectedNextTime, isEmpty, input);
    }

    private static Object[] param(String description, String input, DateTime checkTime, DateTime expectedNextTime, boolean isEmpty, String expectedOutput) {
        return new Object[]{description, input, checkTime, expectedNextTime, isEmpty, expectedOutput};
    }

    @Test
    public void getNextTo() {
        TimeRanges range = TimeRanges.load(this.input);
        assertEquals(
            this.expectedNextTime,
            range.getNextTo(this.checkTime)
        );
    }

    @Test
    public void isEmpty() {
        assertEquals(
                this.isEmpty,
                TimeRanges.load(this.input).isEmpty()
        );
    }

    @Test
    public void save() {
        assertEquals(
                this.expectedOutput,
                TimeRanges.load(this.input).save()
        );

    }


}
