package ru.yandex.autotests.mordabackend.utils.predicates;

import ch.lambdaj.function.matcher.Predicate;
import org.joda.time.format.DateTimeFormat;

/**
 * User: ivannik
 * Date: 29.07.2014
 */
public class ExportDateMatcher extends Predicate<String> {

    public static final String EXPORT_DATE_FORMAT = "yyyy-MM-dd";
    public static final String EXPECTED_DATE_FORMAT = "yyyyMMdd";
    private String targetDateFormat;
    private String expectedDateFormat;
    private String expectedDate;
    private boolean after;

    public ExportDateMatcher(String targetDateFormat, String expectedDateFormat, String expectedDate, boolean after) {
        this.targetDateFormat = targetDateFormat;
        this.expectedDateFormat = expectedDateFormat;
        this.expectedDate = expectedDate;
        this.after = after;
    }

    public static ExportDateMatcher after(String targetDateFormat, String expectedDateFormat, String expectedDate) {
        return new ExportDateMatcher(targetDateFormat, expectedDateFormat, expectedDate, true);
    }

    public static ExportDateMatcher after(String yyyymmdd) {
        return after(EXPORT_DATE_FORMAT, EXPECTED_DATE_FORMAT, yyyymmdd);
    }

    public static ExportDateMatcher before(String targetDateFormat, String expectedDateFormat, String expectedDate) {
        return new ExportDateMatcher(targetDateFormat, expectedDateFormat, expectedDate, false);
    }

    public static ExportDateMatcher before(String yyyymmdd) {
        return before(EXPORT_DATE_FORMAT, EXPECTED_DATE_FORMAT, yyyymmdd);
    }

    @Override
    public boolean apply(String item) {
        if (after) {
            return DateTimeFormat.forPattern(targetDateFormat).parseLocalDateTime(item).compareTo(
                    DateTimeFormat.forPattern(expectedDateFormat).parseLocalDateTime(expectedDate)) >= 0;
        } else {
            return DateTimeFormat.forPattern(targetDateFormat).parseLocalDateTime(item).compareTo(
                    DateTimeFormat.forPattern(expectedDateFormat).parseLocalDateTime(expectedDate)) <= 0;
        }
    }
}
