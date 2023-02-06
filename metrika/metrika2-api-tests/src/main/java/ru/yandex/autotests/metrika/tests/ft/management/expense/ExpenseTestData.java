package ru.yandex.autotests.metrika.tests.ft.management.expense;

import com.google.common.collect.ImmutableMap;
import org.joda.time.LocalDate;

import ru.yandex.metrika.api.management.client.uploading.ExpenseUploadingColumnSettings;

public class ExpenseTestData {

    public static final String CSV_CONTENT = "Date,UTMSource,Expenses\r\n" +
            LocalDate.now().toString("yyyy-MM-dd") + ",facebook,100\r\n";

    public static final String CSV_REMOVE_CONTENT = "Date,UTMSource\r\n" +
            LocalDate.now().toString("yyyy-MM-dd") + ",facebook\r\n";

    public static final String CSV_REMOVE_WITHOUT_DATE_CONTENT = "UTMSource\r\n" +
            "facebook\r\n";

    public static final String CSV_CONTENT_WITH_CYRILIC = "дата,расходы\r\n" +
            LocalDate.now().toString("yyyy-MM-dd") + ",100\r\n";

    public static final String CSV_CONTENT_WITH_CYRILIC_NEGATIVE_EXPENSES = "дата,расходы\r\n" +
            LocalDate.now().toString("yyyy-MM-dd") + ",-100\r\n";

    public static final String DEFAULT_UTM_SOURCE = "facebook";

    private static final ExpenseUploadingColumnSettings DEFAULT_SETTINGS =
            new ExpenseUploadingColumnSettings()
                    .withColumnMappings(ImmutableMap.of("Date", "дата", "Expenses", "расходы"))
                    .withDefaultColumnValues(ImmutableMap.of("UTMSource", DEFAULT_UTM_SOURCE))
                    .withDelimiter(',')
                    .withDecimalDelimiter('.')
                    .withCharset("UTF-8")
            ;

    public static ExpenseUploadingColumnSettings getDefaultSettings() {
        return new ExpenseUploadingColumnSettings()
                .withColumnMappings(DEFAULT_SETTINGS.getColumnMappings())
                .withDefaultColumnValues(DEFAULT_SETTINGS.getDefaultColumnValues())
                .withDelimiter(DEFAULT_SETTINGS.getDelimiter())
                .withDecimalDelimiter(DEFAULT_SETTINGS.getDecimalDelimiter())
                .withCharset("UTF-8")
                ;
    }

    public static final int CSV_CONTENT_SIZE = 1;
    public static final String PROVIDER = "some_provider";
    public static final String COMMENT = "some_comment";
}
