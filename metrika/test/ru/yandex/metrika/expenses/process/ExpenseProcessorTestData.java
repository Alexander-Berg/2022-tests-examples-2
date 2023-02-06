package ru.yandex.metrika.expenses.process;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.Optional;

import ru.yandex.metrika.api.management.client.connectors.AdsPlatform;
import ru.yandex.metrika.api.management.client.external.expense.ExpenseUploading;
import ru.yandex.metrika.api.management.client.external.expense.ExpenseUploadingType;
import ru.yandex.metrika.api.management.client.uploading.ExpenseRemoveUploadingRow;
import ru.yandex.metrika.api.management.client.uploading.ExpenseUploadingRow;
import ru.yandex.metrika.expenses.storage.ExpenseLogRow;
import ru.yandex.metrika.expenses.storage.ExpenseStorageRow;
import ru.yandex.metrika.segments.site.bundles.expenses.ExpensesAttributeBundle;

import static ru.yandex.metrika.api.management.client.external.expense.ExpenseUploadingStatus.UPLOADED;
import static ru.yandex.metrika.util.time.DateTimeUtils.javaToJodaLocalDate;
import static ru.yandex.metrika.util.time.DateTimeUtils.jodaToJavaLocalDate;

public class ExpenseProcessorTestData {

    public static final String BUCKET = "expenses";
    public static final String KEY_PREFIX = "expense_";

    public static final int COUNTER_ID = 1;
    public static final String PROVIDER = "test_provider";

    public static final LocalDate EXPENSE_DATE = LocalDate.of(2020, 9, 1);
    public static final String UTM_SOURCE = "facebook";
    public static final String UTM_MEDIUM = "test_UTMMedium";
    public static final String UTM_CAMPAIGN = "test_UTMCampaign";
    public static final String UTM_TERM = "test_UTMTerm";
    public static final String UTM_CONTENT = "test_UTMContent";
    public static final double EXPENSES = 42.24;
    public static final int CURRENCY_ID = 643;
    public static final int SHOWS = 123;
    public static final int CLICKS = 23;

    public static final int COUNTER_ID_2 = 666;
    public static final String PROVIDER_2 = "test_provider_2";

    public static final LocalDate EXPENSE_DATE_2 = LocalDate.of(2020, 9, 3);
    public static final String UTM_SOURCE_2 = "google";
    public static final String UTM_MEDIUM_2 = "test_UTMMedium_2";
    public static final String UTM_CAMPAIGN_2 = "test_UTMCampaign_2";
    public static final String UTM_TERM_2 = "test_UTMTerm_2";
    public static final String UTM_CONTENT_2 = "test_UTMContent_2";
    public static final double EXPENSES_2 = 24.42;
    public static final int CURRENCY_ID_2 = 840;
    public static final int SHOWS_2 = 234;
    public static final int CLICKS_2 = 32;

    public static ExpenseUploading makeUploading(long id) {
        return makeUploading(id, ExpenseUploadingType.EXPENSES);
    }

    public static ExpenseUploading makeUploading(long id, ExpenseUploadingType type) {
        return makeUploading(
                id,
                type,
                COUNTER_ID,
                PROVIDER
        );
    }

    public static ExpenseUploading makeUploading2(long id) {
        return makeUploading(
                id,
                ExpenseUploadingType.EXPENSES,
                COUNTER_ID_2,
                PROVIDER_2
        );
    }

    private static ExpenseUploading makeUploading(
            long id,
            ExpenseUploadingType type,
            int counterId,
            String provider
    ) {
        ExpenseUploading uploading = new ExpenseUploading();
        uploading.setId(id);
        uploading.setType(type);
        uploading.setCounterId(counterId);
        uploading.setStatus(UPLOADED);
        uploading.setProvider(provider);
        uploading.setBucket(BUCKET);
        uploading.setKey(KEY_PREFIX + id);
        return uploading;
    }

    public static ExpenseUploadingRow makeUploadingRow() {
        return makeUploadingRow(EXPENSE_DATE, EXPENSES, SHOWS, CLICKS);
    }

    public static ExpenseUploadingRow makeUploadingRow(LocalDate date, double expenses, int shows, int clicks) {
        return makeUploadingRow(date, date, expenses, shows, clicks);
    }

    public static ExpenseUploadingRow makeUploadingRow(LocalDate dateFrom, LocalDate dateTo, double expenses, int shows, int clicks) {
        return makeUploadingRow(
                dateFrom, dateTo,
                UTM_SOURCE, UTM_MEDIUM, UTM_CAMPAIGN, UTM_TERM, UTM_CONTENT,
                expenses, CURRENCY_ID,
                shows, clicks
        );
    }

    public static ExpenseUploadingRow makeUploadingRow2() {
        return makeUploadingRow(
                EXPENSE_DATE_2, EXPENSE_DATE_2,
                UTM_SOURCE_2, UTM_MEDIUM_2, UTM_CAMPAIGN_2, UTM_TERM_2, UTM_CONTENT_2,
                EXPENSES_2, CURRENCY_ID_2 ,
                SHOWS_2, CLICKS_2
        );
    }

    private static ExpenseUploadingRow makeUploadingRow(
            LocalDate dateFrom, LocalDate dateTo,
            String utmSource, String utmMedium, String utmCampaign, String utmTerm, String utmContent,
            double expenses, int currencyId,
            int shows, int clicks
    ) {
        return new ExpenseUploadingRow(
                javaToJodaLocalDate(dateFrom), javaToJodaLocalDate(dateTo),
                utmSource, utmMedium, utmCampaign, utmTerm, utmContent,
                BigDecimal.valueOf(expenses), currencyId,
                shows, clicks
        );
    }

    public static ExpenseRemoveUploadingRow makeRemoveUploadingRow() {
        return new ExpenseRemoveUploadingRow(
                javaToJodaLocalDate(EXPENSE_DATE),
                javaToJodaLocalDate(EXPENSE_DATE),
                UTM_SOURCE, UTM_MEDIUM, UTM_CAMPAIGN, UTM_TERM, UTM_CONTENT
        );
    }

    public static ExpenseStorageRow makeExpenseStorageRow(
            ExpenseUploading uploading, ExpenseUploadingRow uploadingRow,
            int version
    ) {
        return makeExpenseStorageRow(
                uploading, uploadingRow, jodaToJavaLocalDate(uploadingRow.dateFrom()),
                version,
                uploadingRow.expenses().doubleValue(), uploadingRow.shows(), uploadingRow.clicks()
        );
    }

    public static ExpenseStorageRow makeExpenseStorageRow(
            ExpenseUploading uploading, ExpenseUploadingRow uploadingRow, LocalDate date,
            int version,
            double expenses, int shows, int clicks
    ) {
        return new ExpenseStorageRow(
                (int) uploading.getCounterId(),
                Optional.ofNullable(uploading.getAdsPlatform()).map(AdsPlatform::id).orElse(0).byteValue(),
                Optional.ofNullable(uploading.getCustomerAccountId()).orElse(0L),
                date,
                uploadingRow.utmSource(), uploadingRow.utmMedium(), uploadingRow.utmCampaign(), uploadingRow.utmTerm(), uploadingRow.utmContent(),
                version,
                (int) uploading.getId(),
                uploading.getProvider(),
                multiplyExpenses(expenses), uploadingRow.currencyId(),
                shows, clicks
        );
    }

    public static ExpenseLogRow makeExpenseLogRow(
            ExpenseUploading uploading, ExpenseUploadingRow uploadingRow,
            int version, int sign
    ) {
        return makeExpenseLogRow(
                uploading, uploadingRow, jodaToJavaLocalDate(uploadingRow.dateFrom()),
                version, sign,
                uploadingRow.expenses().doubleValue(), uploadingRow.shows(), uploadingRow.clicks()
        );
    }

    public static ExpenseLogRow makeExpenseLogRow(
            ExpenseUploading uploading, ExpenseUploadingRow uploadingRow, LocalDate date,
            int version, int sign,
            double expenses, int shows, int clicks
    ) {
        return new ExpenseLogRow(
                (int) uploading.getCounterId(),
                date,
                Optional.ofNullable(uploading.getAdsPlatform()).map(AdsPlatform::id).orElse(0).byteValue(),
                Optional.ofNullable(uploading.getCustomerAccountId()).orElse(0L),
                uploadingRow.utmSource(), uploadingRow.utmMedium(), uploadingRow.utmCampaign(), uploadingRow.utmTerm(), uploadingRow.utmContent(),
                version,
                (byte) sign,
                (int) uploading.getId(),
                uploading.getProvider(),
                multiplyExpenses(expenses), uploadingRow.currencyId(),
                shows, clicks
        );
    }

    public static long multiplyExpenses(double expenses) {
        return (long) (expenses * ExpensesAttributeBundle.EXPENSES_MULTIPLIER);
    }
}
