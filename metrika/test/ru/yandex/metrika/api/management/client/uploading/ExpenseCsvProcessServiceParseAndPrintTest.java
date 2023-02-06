package ru.yandex.metrika.api.management.client.uploading;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.Arrays;
import java.util.Collection;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import org.joda.time.LocalDate;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;

import ru.yandex.metrika.api.management.client.counter.CountersDao;
import ru.yandex.metrika.managers.CurrencyService;
import ru.yandex.metrika.util.csv.CSVParseResult;
import ru.yandex.metrika.util.locale.LocaleDictionaries;
import ru.yandex.metrika.util.time.DateTimeFormatters;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Matchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

@RunWith(Parameterized.class)
public class ExpenseCsvProcessServiceParseAndPrintTest {

    public static final int MAX_UTM_SIZE = 4096;

    private static final String TODAY = DateTimeFormatters.ISO_DTF.print(LocalDate.now());

    private static final String GOOD_CSV = "" +
            "Date,UTMSource,Expenses\r\n" +
            TODAY + ",facebook,100\r\n";

    private static final String GOOD_CSV_REORDERED = "" +
            "UTMSource,Expenses,Date\r\n" +
            "facebook,100," + TODAY + "\r\n";

    private static final String GOOD_CSV_EXTRA_COLUMN = "" +
            "Date,UTMSource,Trash,Expenses\r\n" +
            TODAY + ",facebook,bbb,100\r\n";

    private static final String GOOD_CSV_EXPECTED = "" +
            "DateFrom,DateTo,UTMSource,UTMMedium,UTMCampaign,UTMTerm,UTMContent,Expenses,CurrencyID,Shows,Clicks\r\n" +
            TODAY + "," + TODAY + ",facebook,,,,,100,643,0,0\r\n";

    private static final String LONG_UTM_INPUT = "" +
            "Date,UTMSource,Expenses\r\n" +
            TODAY + "," + "A".repeat(MAX_UTM_SIZE + 1) + ",100\r\n";

    private static final String LONG_UTM_EXPECTED = "" +
            "DateFrom,DateTo,UTMSource,UTMMedium,UTMCampaign,UTMTerm,UTMContent,Expenses,CurrencyID,Shows,Clicks\r\n" +
            TODAY + "," + TODAY + "," + "A".repeat(MAX_UTM_SIZE) + ",,,,,100,643,0,0\r\n";

    @Parameter
    public String description;
    @Parameter(1)
    public String input;
    @Parameter(2)
    public String expected;

    private ExecutorService executor;
    private ByteArrayOutputStream formattedCsvOutputStream;

    @Parameters(name = "{0}")
    public static Collection<String[]> data() {
        return Arrays.asList(
                new String[]{"good csv", GOOD_CSV, GOOD_CSV_EXPECTED},
                new String[]{"re-ordered columns", GOOD_CSV_REORDERED, GOOD_CSV_EXPECTED},
                new String[]{"remove unexpected column", GOOD_CSV_EXTRA_COLUMN, GOOD_CSV_EXPECTED},
                new String[]{"truncates long UTM", LONG_UTM_INPUT, LONG_UTM_EXPECTED});
    }

    @Before
    public void setUp() {
        executor = Executors.newFixedThreadPool(1);
        formattedCsvOutputStream = new ByteArrayOutputStream();
    }

    @After
    public void tearDown() throws IOException {
        formattedCsvOutputStream.close();
        executor.shutdown();
    }

    @Test
    public void csvParseAndPrint() {
        printInService(input);
        String res = new String(formattedCsvOutputStream.toByteArray());
        assertThat(res).isEqualTo(expected);
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

        ExpenseUploadingStorage expenseUploadingStorage = new ExpenseUploadingStorage();

        try (CSVParseResult<ExpenseUploadingRow> rows =
                     expenseCsvProcessService.process(1, new ByteArrayInputStream(data.getBytes()))) {
            expenseUploadingStorage.writeExpensesToStorage(rows.iterator(), formattedCsvOutputStream);
        }
    }
}
