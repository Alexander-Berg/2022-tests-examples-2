package ru.yandex.metrika.api.management.client.uploading;

import java.io.ByteArrayInputStream;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.api.management.client.counter.CountersDao;
import ru.yandex.metrika.managers.CurrencyService;
import ru.yandex.metrika.util.csv.CSVParseException;
import ru.yandex.metrika.util.csv.CSVParseResult;
import ru.yandex.metrika.util.locale.LocaleDictionaries;

import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Matchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

public class ExpenseCsvProcessServiceValidationTest {

    private ExecutorService executor;

    @Before
    public void setUp() {
        executor = Executors.newSingleThreadExecutor();
    }

    @After
    public void tearDown() {
        executor.shutdown();
    }

    @Test
    public void failsWhenInvalidDateFormat() {
        assertThatThrownBy(() -> printInService(ExpenseCsvSampleData.INVALID_DATE))
                .isExactlyInstanceOf(CSVParseException.class);
    }

    @Test
    public void failsWhenInvalidDateMultiple() {
        assertThatThrownBy(() -> printInService(ExpenseCsvSampleData.INVALID_DATE_MULTIPLE))
                .isExactlyInstanceOf(CSVParseException.class);
    }

    @Test
    public void failsWhenInvalidExpensesData() {
        assertThatThrownBy(() -> printInService(ExpenseCsvSampleData.INVALID_EXPENSES))
                .isExactlyInstanceOf(CSVParseException.class);
    }

    @Test
    public void failsWhenNoValueInExpensesColumn() {
        assertThatThrownBy(() -> printInService(ExpenseCsvSampleData.INVALID_NO_VALUE_IN_REQUIRED_DATE_COLUMN))
                .isExactlyInstanceOf(CSVParseException.class);
    }

    @Test
    public void successWhenValidData() {
        printInService(ExpenseCsvSampleData.VALID_DATA);
    }

    @Test
    public void successWhenValidDataWithAdditionalColumns() {
        printInService(ExpenseCsvSampleData.VALID_DATA_BIG_W_EXTRA_COLUMNS);
    }

    @Test
    public void failsWhenNoRequiredUtmSourceColumns() {
        assertThatThrownBy(() -> printInService(ExpenseCsvSampleData.INVALID_NO_REQUIRED_UTMSOURCE_CSV))
                .isExactlyInstanceOf(CSVParseException.class);
    }

    @Test
    public void failsWhenNoRequiredExpensesColumn() {
        assertThatThrownBy(() -> printInService(ExpenseCsvSampleData.INVALID_NO_REQUIRED_EXPENSES_COLUMN))
                .isExactlyInstanceOf(CSVParseException.class);
    }

    @Test
    public void failsWhenNoRequiredDateColumn() {
        assertThatThrownBy(() -> printInService(ExpenseCsvSampleData.INVALID_NO_REQUIRED_DATE_COLUMN))
                .isExactlyInstanceOf(CSVParseException.class);
    }

    @Test
    public void failsWhenNoRequiredUtmSourceAndExpensesColumns() {
        assertThatThrownBy(() -> printInService(ExpenseCsvSampleData.INVALID_NO_REQUIRED_UTMSOURCE_AND_EXPENSES_CSV))
                .isExactlyInstanceOf(CSVParseException.class);
    }

    private void printInService(String data) {
        CurrencyService currencyService = mock(CurrencyService.class);
        when(currencyService.getCurrenciesMap3Int()).thenReturn(Map.of("RUB", 643));

        CountersDao countersDao = mock(CountersDao.class);
        when(countersDao.getCurrency(any())).thenReturn("RUB");

        LocaleDictionaries localeDictionaries = mock(LocaleDictionaries.class);

        ExpenseCsvProcessService expenseCsvProcessService = new ExpenseCsvProcessService(
                currencyService,
                countersDao,
                localeDictionaries
        );

        try (CSVParseResult<ExpenseUploadingRow> rows =
                     expenseCsvProcessService.process(1, new ByteArrayInputStream(data.getBytes()))) {
            rows.iterator().forEachRemaining(row -> {});
        }
    }
}
