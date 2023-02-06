package ru.yandex.metrika.expenses.process;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.time.LocalDate;
import java.util.List;
import java.util.Set;
import java.util.stream.IntStream;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.metrika.api.management.client.external.expense.ExpenseUploading;
import ru.yandex.metrika.api.management.client.external.expense.ExpenseUploadingStatus;
import ru.yandex.metrika.api.management.client.external.expense.ExpenseUploadingType;
import ru.yandex.metrika.api.management.client.uploading.ExpenseRemoveUploadingRow;
import ru.yandex.metrika.api.management.client.uploading.ExpenseUploadingMetadataService;
import ru.yandex.metrika.api.management.client.uploading.ExpenseUploadingRow;
import ru.yandex.metrika.api.management.client.uploading.ExpenseUploadingStorage;
import ru.yandex.metrika.expenses.storage.InMemoryExpenseLogStorage;
import ru.yandex.metrika.expenses.storage.InMemoryExpenseStorage;
import ru.yandex.metrika.managers.CurrencyRateConverter;
import ru.yandex.metrika.util.chunk.mds.MdsChunkStorage;
import ru.yandex.metrika.util.log.Log4jSetup;

import static org.hamcrest.Matchers.contains;
import static org.hamcrest.Matchers.containsInAnyOrder;
import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.notNullValue;
import static org.junit.Assert.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyCollection;
import static org.mockito.ArgumentMatchers.anyDouble;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.doCallRealMethod;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static ru.yandex.metrika.api.management.client.uploading.ExpenseUploadingStorage.COLUMN_DATE_FROM;
import static ru.yandex.metrika.api.management.client.uploading.ExpenseUploadingStorage.COLUMN_DATE_TO;
import static ru.yandex.metrika.api.management.client.uploading.ExpenseUploadingStorage.COLUMN_UTM_CAMPAIGN;
import static ru.yandex.metrika.api.management.client.uploading.ExpenseUploadingStorage.COLUMN_UTM_CONTENT;
import static ru.yandex.metrika.api.management.client.uploading.ExpenseUploadingStorage.COLUMN_UTM_MEDIUM;
import static ru.yandex.metrika.api.management.client.uploading.ExpenseUploadingStorage.COLUMN_UTM_SOURCE;
import static ru.yandex.metrika.api.management.client.uploading.ExpenseUploadingStorage.COLUMN_UTM_TERM;
import static ru.yandex.metrika.expenses.process.ExpenseProcessorTestData.makeExpenseLogRow;
import static ru.yandex.metrika.expenses.process.ExpenseProcessorTestData.makeExpenseStorageRow;
import static ru.yandex.metrika.expenses.process.ExpenseProcessorTestData.makeRemoveUploadingRow;
import static ru.yandex.metrika.expenses.process.ExpenseProcessorTestData.makeUploading;
import static ru.yandex.metrika.expenses.process.ExpenseProcessorTestData.makeUploading2;
import static ru.yandex.metrika.expenses.process.ExpenseProcessorTestData.makeUploadingRow;
import static ru.yandex.metrika.expenses.process.ExpenseProcessorTestData.makeUploadingRow2;

public class ExpenseProcessorTest {

    private ExpenseUploadingMetadataService uploadingMetadataService;
    private MdsChunkStorage uploadingChunkStorage;
    private ExpenseUploadingStorage uploadingStorage;
    private InMemoryExpenseStorage expenseStorage;
    private InMemoryExpenseLogStorage expenseLogStorage;
    private ExpenseProcessor expenseProcessor;

    private int expenseProcessingBatchSize = 10;

    @BeforeClass
    public static void initClass() {
        Log4jSetup.basicSetup();
    }

    @Before
    public void init() {
        uploadingMetadataService = mock(ExpenseUploadingMetadataService.class);
        uploadingChunkStorage = mock(MdsChunkStorage.class);
        CurrencyRateConverter currencyRateConverter = mock(CurrencyRateConverter.class);
        when(currencyRateConverter.convert(any(), anyInt(), anyInt(), anyDouble()))
                .thenAnswer(invocation -> invocation.getArgument(3, Double.class));

        uploadingStorage = new ExpenseUploadingStorage();

        expenseStorage = spy(new InMemoryExpenseStorage());
        expenseLogStorage = spy(new InMemoryExpenseLogStorage());
        expenseProcessor = new ExpenseProcessor(
                uploadingMetadataService,
                uploadingChunkStorage,
                uploadingStorage,
                expenseStorage,
                expenseLogStorage,
                currencyRateConverter
        );
        expenseProcessor.setExpenseBatchSize(expenseProcessingBatchSize);
        expenseProcessor.setExpenseRemoveBatchSize(expenseProcessingBatchSize);
    }

    @Test
    public void testSimple() {
        ExpenseUploading uploading = makeUploading(1L);
        ExpenseUploadingRow uploadingRow = makeUploadingRow();
        processUploading(uploading, List.of(uploadingRow));

        assertThat(expenseStorage.getData(), containsInAnyOrder(
                makeExpenseStorageRow(uploading, uploadingRow, 1)
        ));
        assertThat(expenseStorage.getUploadingOffset(1), equalTo(1));
        assertThat(expenseLogStorage.getData(), contains(
                makeExpenseLogRow(uploading, uploadingRow, 1, 1)
        ));
    }

    @Test
    public void testMultipleRows() {
        ExpenseUploading uploading = makeUploading(1L);
        ExpenseUploadingRow uploadingRow1 = makeUploadingRow();
        ExpenseUploadingRow uploadingRow2 = makeUploadingRow2();
        processUploading(uploading, List.of(uploadingRow1, uploadingRow2));

        assertThat(expenseStorage.getData(), containsInAnyOrder(
                makeExpenseStorageRow(uploading, uploadingRow1, 1),
                makeExpenseStorageRow(uploading, uploadingRow2, 1)
        ));
        assertThat(expenseStorage.getUploadingOffset(1), equalTo(2));
        assertThat(expenseLogStorage.getData(), contains(
                makeExpenseLogRow(uploading, uploadingRow1, 1, 1),
                makeExpenseLogRow(uploading, uploadingRow2, 1, 1)
        ));
    }

    @Test
    public void testMultipleRowsWithSameKey() {
        LocalDate date = LocalDate.of(2020, 9, 1);

        double expenses1 = 42.24;
        int shows1 = 123;
        int clicks1 = 23;

        double expenses2 = 24.42;
        int shows2 = 234;
        int clicks2 = 32;

        ExpenseUploading uploading = makeUploading(1L);
        ExpenseUploadingRow uploadingRow1 = makeUploadingRow(date, expenses1, shows1, clicks1);
        ExpenseUploadingRow uploadingRow2 = makeUploadingRow(date, expenses2, shows2, clicks2);
        processUploading(uploading, List.of(uploadingRow1, uploadingRow2));

        double expensesTotal = 66.66;
        int showsTotal = 357;
        int clicksTotal = 55;

        assertThat(expenseStorage.getData(), containsInAnyOrder(
                makeExpenseStorageRow(uploading, uploadingRow1, date, 1, expensesTotal, showsTotal, clicksTotal)
        ));
        assertThat(expenseStorage.getUploadingOffset(1), equalTo(2));
        assertThat(expenseLogStorage.getData(), contains(
                makeExpenseLogRow(uploading, uploadingRow1, date, 1, 1, expensesTotal, showsTotal, clicksTotal)
        ));
    }

    @Test
    public void testDateRange() {
        LocalDate dateFrom = LocalDate.of(2020, 9, 1);
        LocalDate dateTo = LocalDate.of(2020, 9, 3);
        double expenses = 60;
        int shows = 90;
        int clicks = 30;

        ExpenseUploading uploading = makeUploading(1L);
        ExpenseUploadingRow uploadingRow = makeUploadingRow(dateFrom, dateTo, expenses, shows, clicks);
        processUploading(uploading, List.of(uploadingRow));

        LocalDate date1 = LocalDate.of(2020, 9, 1);
        LocalDate date2 = LocalDate.of(2020, 9, 2);
        LocalDate date3 = LocalDate.of(2020, 9, 3);
        double expensesPerDay = 20;
        int showsPerDay = 30;
        int clicksPerDay = 10;

        assertThat(expenseStorage.getData(), containsInAnyOrder(
                makeExpenseStorageRow(uploading, uploadingRow, date1, 1, expensesPerDay, showsPerDay, clicksPerDay),
                makeExpenseStorageRow(uploading, uploadingRow, date2, 1, expensesPerDay, showsPerDay, clicksPerDay),
                makeExpenseStorageRow(uploading, uploadingRow, date3, 1, expensesPerDay, showsPerDay, clicksPerDay)
        ));
        assertThat(expenseStorage.getUploadingOffset(1), equalTo(3));
        assertThat(expenseLogStorage.getData(), contains(
                makeExpenseLogRow(uploading, uploadingRow, date1, 1, 1, expensesPerDay, showsPerDay, clicksPerDay),
                makeExpenseLogRow(uploading, uploadingRow, date2, 1, 1, expensesPerDay, showsPerDay, clicksPerDay),
                makeExpenseLogRow(uploading, uploadingRow, date3, 1, 1, expensesPerDay, showsPerDay, clicksPerDay)
        ));
    }

    @Test
    public void testMultipleUploadings() {
        ExpenseUploading uploading1 = makeUploading(1L);
        ExpenseUploadingRow uploadingRow1 = makeUploadingRow();
        processUploading(uploading1, List.of(uploadingRow1));

        ExpenseUploading uploading2 = makeUploading2(2L);
        ExpenseUploadingRow uploadingRow2 = makeUploadingRow2();
        processUploading(uploading2, List.of(uploadingRow2));

        assertThat(expenseStorage.getData(), containsInAnyOrder(
                makeExpenseStorageRow(uploading1, uploadingRow1, 1),
                makeExpenseStorageRow(uploading2, uploadingRow2, 1)
        ));
        assertThat(expenseStorage.getUploadingOffset(1), equalTo(1));
        assertThat(expenseStorage.getUploadingOffset(2), equalTo(1));
        assertThat(expenseLogStorage.getData(), contains(
                makeExpenseLogRow(uploading1, uploadingRow1, 1, 1),
                makeExpenseLogRow(uploading2, uploadingRow2, 1, 1)
        ));
    }

    @Test
    public void testUpdate() {
        LocalDate date = LocalDate.of(2020, 9, 1);
        double expenses = 42.24;
        int shows = 123;
        int clicks = 23;

        ExpenseUploading uploading1 = makeUploading(1L);
        ExpenseUploadingRow uploadingRow1 = makeUploadingRow(date, expenses, shows, clicks);
        processUploading(uploading1, List.of(uploadingRow1));

        double newExpenses = 24.42;
        int newShows = 234;
        int newClicks = 32;

        ExpenseUploading uploading2 = makeUploading(2L);
        ExpenseUploadingRow uploadingRow2 = makeUploadingRow(date, newExpenses, newShows, newClicks);
        processUploading(uploading2, List.of(uploadingRow2));

        assertThat(expenseStorage.getData(), containsInAnyOrder(
                makeExpenseStorageRow(uploading2, uploadingRow2, 2)
        ));
        assertThat(expenseStorage.getUploadingOffset(1), equalTo(1));
        assertThat(expenseStorage.getUploadingOffset(2), equalTo(1));
        assertThat(expenseLogStorage.getData(), contains(
                makeExpenseLogRow(uploading1, uploadingRow1, 1, 1),
                makeExpenseLogRow(uploading1, uploadingRow1, 1, -1),
                makeExpenseLogRow(uploading2, uploadingRow2, 2, 1)
        ));
    }

    @Test
    public void testRemove() {
        ExpenseUploading uploading1 = makeUploading(1L);
        ExpenseUploadingRow uploadingRow = makeUploadingRow();
        processUploading(uploading1, List.of(uploadingRow));

        ExpenseUploading uploading2 = makeUploading(2L, ExpenseUploadingType.REMOVES);
        ExpenseRemoveUploadingRow removeUploadingRow = makeRemoveUploadingRow();
        processRemoveUploading(uploading2, List.of(removeUploadingRow));

        assertThat(expenseStorage.getData(), empty());
        assertThat(expenseStorage.getUploadingOffset(1), equalTo(1));
        assertThat(expenseStorage.getUploadingOffset(2), equalTo(1));
        assertThat(expenseLogStorage.getData(), contains(
                makeExpenseLogRow(uploading1, uploadingRow, 1, 1),
                makeExpenseLogRow(uploading1, uploadingRow, 1, -1)
        ));
    }

    @Test
    public void testRetry() {
        LocalDate date = LocalDate.of(2020, 9, 1);
        int rowsAmount = 17;
        double expensesPerRow = 2d;
        int showsPerRow = 5;
        int clicksPerRow = 3;
        long uploadingId = 1L;

        ExpenseUploading uploading = makeUploading(uploadingId);
        List<ExpenseUploadingRow> uploadingRows = IntStream.range(0, rowsAmount)
                .mapToObj(i -> makeUploadingRow(date, expensesPerRow, showsPerRow, clicksPerRow))
                .toList();

        // кидаем исключение на второй пачке
        doCallRealMethod().doThrow(new RuntimeException()).when(expenseStorage).save(anyCollection(), anyInt(), anyInt());
        Exception actualException = null;
        try {
            processUploading(uploading, uploadingRows);
        } catch (Exception e) {
            actualException = e;
        }

        assertThat(actualException, notNullValue());

        // вызываем обработку еще раз
        doCallRealMethod().when(expenseStorage).save(anyCollection(), anyInt(), anyInt());
        processUploading(uploading, uploadingRows);

        assertThat(expenseStorage.getData(), containsInAnyOrder(
                makeExpenseStorageRow(uploading, uploadingRows.get(0), date, 2, expensesPerRow * rowsAmount, showsPerRow * rowsAmount, clicksPerRow * rowsAmount)
        ));
        assertThat(expenseStorage.getUploadingOffset((int) uploadingId), equalTo(rowsAmount));
        assertThat(expenseLogStorage.getData(), contains(
                makeExpenseLogRow(uploading, uploadingRows.get(0), date, 1,  1, expensesPerRow * expenseProcessingBatchSize, showsPerRow * expenseProcessingBatchSize, clicksPerRow * expenseProcessingBatchSize),
                makeExpenseLogRow(uploading, uploadingRows.get(0), date, 1, -1, expensesPerRow * expenseProcessingBatchSize, showsPerRow * expenseProcessingBatchSize, clicksPerRow * expenseProcessingBatchSize),
                makeExpenseLogRow(uploading, uploadingRows.get(0), date, 2,  1, expensesPerRow * rowsAmount, showsPerRow * rowsAmount, clicksPerRow * rowsAmount)
        ));
    }

    private void processUploading(ExpenseUploading uploading, List<ExpenseUploadingRow> uploadingRows) {
        when(uploadingChunkStorage.load(anyString(), anyString())).thenReturn(makeUploadingData(uploadingRows));
        expenseProcessor.processUploading(uploading);
        verify(uploadingMetadataService).updateStatus(uploading.getId(), ExpenseUploadingStatus.PROCESSED);
    }

    private void processRemoveUploading(ExpenseUploading uploading, List<ExpenseRemoveUploadingRow> removeUploadingRows) {
        when(uploadingChunkStorage.load(anyString(), anyString())).thenReturn(makeRemoveUploadingData(removeUploadingRows));
        expenseProcessor.processUploading(uploading);
        verify(uploadingMetadataService).updateStatus(uploading.getId(), ExpenseUploadingStatus.PROCESSED);
    }

    private ByteArrayInputStream makeUploadingData(List<ExpenseUploadingRow> rows) {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        uploadingStorage.writeExpensesToStorage(rows.iterator(), baos);
        return new ByteArrayInputStream(baos.toByteArray());
    }

    private ByteArrayInputStream makeRemoveUploadingData(List<ExpenseRemoveUploadingRow> rows) {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        uploadingStorage.writeExpensesRemoveToStorage(rows.iterator(), baos, Set.of(
                COLUMN_DATE_FROM, COLUMN_DATE_TO,
                COLUMN_UTM_SOURCE, COLUMN_UTM_MEDIUM, COLUMN_UTM_CAMPAIGN, COLUMN_UTM_TERM, COLUMN_UTM_CONTENT
        ));
        return new ByteArrayInputStream(baos.toByteArray());
    }
}
