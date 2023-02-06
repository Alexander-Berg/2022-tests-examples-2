package ru.yandex.metrika.expenses.process;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.Spliterator;
import java.util.Spliterators;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import ru.yandex.metrika.expenses.connectors.AdsConnectorsStateStorage;
import ru.yandex.metrika.expenses.connectors.AdsReportProcessor;
import ru.yandex.metrika.expenses.connectors.google.GoogleExpensesRow;
import ru.yandex.metrika.expenses.connectors.google.GoogleExpensesYdbKey;
import ru.yandex.metrika.expenses.connectors.google.GoogleExpensesYdbRow;
import ru.yandex.metrika.expenses.storage.AdsConnectorsStateStorageInMemory;
import ru.yandex.metrika.util.log.Log4jSetup;

import static java.util.stream.Collectors.toMap;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

public class AdsReportProcessorTest {

    private AdsReportProcessor reportProcessor;
    private AdsConnectorsStateStorageInMemory<GoogleExpensesYdbRow> storage;

    @BeforeClass
    public static void initClass() {
        Log4jSetup.basicSetup();
    }

    @Before
    public void init() {
        storage = new AdsConnectorsStateStorageInMemory<>();
        //noinspection rawtypes
        reportProcessor = new AdsReportProcessor((AdsConnectorsStateStorage) storage);

        storage.save(
                // here and further we rely on both all_valid_rows.tskv and new_report.tskv
                // contain data only for CustomerId = 7 and Date = 2021-02-01
                loadGoogleExpenseRowFulls("all_valid_rows.tskv")
                        .stream()
                        .map(GoogleExpensesRow::toYdbRow)
                        .collect(Collectors.toList())
        );
    }

    @Test
    // sanity test to make sure that further business logic tests won't be affected by bugs in InMemory storage
    public void testStorage() {
        List<GoogleExpensesRow> newReport = loadGoogleExpenseRowFulls("new_report.tskv");

        reportProcessor.process(newReport.iterator());

        assertEquals(
                storage.getAllRows()
                        .stream()
                        .filter(GoogleExpensesYdbRow::isDeleted)
                        .map(GoogleExpensesYdbRow::getAdGroupAdAdId)
                        .collect(Collectors.toSet()),
                StreamSupport.stream(
                        Spliterators.spliteratorUnknownSize(
                                storage.load(7, LocalDate.parse("2021-02-01"), true),
                                Spliterator.ORDERED
                        ),
                        false
                ).map(GoogleExpensesYdbRow::getAdGroupAdAdId).collect(Collectors.toSet())
        );

        assertEquals(
                storage.getAllRows()
                        .stream()
                        .filter(r -> !r.isDeleted())
                        .map(GoogleExpensesYdbRow::getAdGroupAdAdId)
                        .collect(Collectors.toSet()),
                StreamSupport.stream(
                        Spliterators.spliteratorUnknownSize(
                                storage.load(7, LocalDate.parse("2021-02-01"), false),
                                Spliterator.ORDERED
                        ),
                        false
                ).map(GoogleExpensesYdbRow::getAdGroupAdAdId).collect(Collectors.toSet())
        );

        assertEquals(
                storage.getAllRows()
                        .stream()
                        .map(GoogleExpensesYdbRow::getAdGroupAdAdId)
                        .collect(Collectors.toSet()),
                StreamSupport.stream(
                        Spliterators.spliteratorUnknownSize(
                                storage.readTable(7L, LocalDate.parse("2021-02-01")),
                                Spliterator.ORDERED
                        ),
                        false
                ).map(GoogleExpensesYdbRow::getAdGroupAdAdId).collect(Collectors.toSet())
        );
    }

    @Test
    public void testUpdate() {
        List<GoogleExpensesRow> newReport = loadGoogleExpenseRowFulls("new_report.tskv");

        Map<Long, GoogleExpensesYdbRow> update = newReport.stream()
                .map(GoogleExpensesRow::toYdbRow)
                .collect(toMap(GoogleExpensesYdbRow::getAdGroupAdAdId, r -> r));

        reportProcessor.process(newReport.iterator());

        Map<Long, GoogleExpensesYdbRow> updated = storage.getAllRows()
                .stream()
                .collect(toMap(GoogleExpensesYdbRow::getAdGroupAdAdId, r -> r));

        assertEquals(
                "Impressions are updated",
                update.get(181329323661L).getImpressions(),
                updated.get(181329323661L).getImpressions()
        );
        assertEquals(
                "Clicks are updated",
                update.get(178394009434L).getClicks(),
                updated.get(178394009434L).getClicks()
        );
        assertEquals(
                "Costs are updated",
                update.get(197948574670L).getCostMicros(),
                updated.get(197948574670L).getCostMicros()
        );
        assertTrue(
                "All metrics are updated",
                List.of(
                        update.get(191040815458L).getImpressions().equals(updated.get(191040815458L).getImpressions()),
                        update.get(191040815458L).getClicks().equals(updated.get(191040815458L).getClicks()),
                        update.get(191040815458L).getCostMicros().equals(updated.get(191040815458L).getCostMicros())
                ).stream().allMatch(b -> b)
        );
    }

    @Test
    public void testInsert() {
        List<GoogleExpensesRow> newReport = loadGoogleExpenseRowFulls("new_report.tskv");

        Map<GoogleExpensesYdbKey, GoogleExpensesYdbRow> original = storage.getAllRows()
                .stream()
                .collect(toMap(GoogleExpensesYdbRow::getId, r -> r));
        Map<Long, GoogleExpensesYdbRow> update = newReport.stream()
                .map(GoogleExpensesRow::toYdbRow)
                .collect(toMap(GoogleExpensesYdbRow::getAdGroupAdAdId, r -> r));

        reportProcessor.process(newReport.iterator());

        Map<GoogleExpensesYdbKey, GoogleExpensesYdbRow> updated = storage.getAllRows()
                .stream()
                .collect(toMap(GoogleExpensesYdbRow::getId, r -> r));

        assertFalse(original.containsKey(update.get(978271565337L).getId()));
        assertFalse(original.containsKey(update.get(324531666611L).getId()));

        assertTrue(updated.containsKey(update.get(978271565337L).getId()));
        assertTrue(updated.containsKey(update.get(324531666611L).getId()));

        assertEquals(4690000L, updated.get(update.get(978271565337L).getId()).getCostMicros().longValue());
        assertEquals(44600000L, updated.get(update.get(324531666611L).getId()).getCostMicros().longValue());

        assertEquals(3L, updated.get(update.get(978271565337L).getId()).getImpressions().longValue());
        assertEquals(1L, updated.get(update.get(324531666611L).getId()).getImpressions().longValue());

        assertEquals(1L, updated.get(update.get(978271565337L).getId()).getClicks().longValue());
        assertEquals(1L, updated.get(update.get(324531666611L).getId()).getClicks().longValue());
    }

    @Test
    public void testDelete() {
        List<GoogleExpensesRow> newReport = loadGoogleExpenseRowFulls("new_report.tskv");

        Map<Long, GoogleExpensesYdbRow> original = storage.getAllRows()
                .stream()
                .collect(toMap(GoogleExpensesYdbRow::getAdGroupAdAdId, r -> r));
        Map<Long, GoogleExpensesYdbRow> update = newReport.stream()
                .map(GoogleExpensesRow::toYdbRow)
                .collect(toMap(GoogleExpensesYdbRow::getAdGroupAdAdId, r -> r));

        reportProcessor.process(newReport.iterator());

        Set<Long> deletedAdGroupAdAdId = storage.getAllRows()
                .stream()
                .filter(GoogleExpensesYdbRow::isDeleted)
                .map(GoogleExpensesYdbRow::getAdGroupAdAdId)
                .collect(Collectors.toSet());

        assertTrue(original.containsKey(181329323643L) && !update.containsKey(181329323643L) && deletedAdGroupAdAdId.contains(181329323643L));
        assertTrue(original.containsKey(178271565337L) && !update.containsKey(178271565337L) && deletedAdGroupAdAdId.contains(178271565337L));
        assertTrue(original.containsKey(324531666610L) && !update.containsKey(324531666610L) && deletedAdGroupAdAdId.contains(324531666610L));
        assertTrue(original.containsKey(184441445518L) && !update.containsKey(184441445518L) && deletedAdGroupAdAdId.contains(184441445518L));
        assertTrue(original.containsKey(211560036927L) && !update.containsKey(211560036927L) && deletedAdGroupAdAdId.contains(211560036927L));
    }

    @Test
    public void testRetain() {
        List<GoogleExpensesRow> newReport = loadGoogleExpenseRowFulls("new_report.tskv");

        reportProcessor.process(newReport.iterator());

        Map<Long, GoogleExpensesYdbRow> updated = storage.getAllRows()
                .stream()
                .collect(toMap(GoogleExpensesYdbRow::getAdGroupAdAdId, r -> r));

        assertTrue(
                updated.keySet().containsAll(
                        List.of(
                                189690552887L,
                                400261199215L,
                                211560037134L,
                                397582312057L,
                                397565145777L,
                                421575430471L,
                                211560036888L,
                                211560036894L,
                                211560036921L,
                                211560037089L,
                                211560036924L
                        )
                )
        );
        assertEquals(140030000L, updated.get(189690552887L).getCostMicros().longValue());
        assertEquals(100280000L, updated.get(400261199215L).getCostMicros().longValue());
        assertEquals(24090000L, updated.get(211560037134L).getCostMicros().longValue());
        assertEquals(54580000L, updated.get(397582312057L).getCostMicros().longValue());
        assertEquals(4560000L, updated.get(397565145777L).getCostMicros().longValue());
        assertEquals(1275010000L, updated.get(421575430471L).getCostMicros().longValue());
        assertEquals(62620000L, updated.get(211560036888L).getCostMicros().longValue());
        assertEquals(22720000L, updated.get(211560036894L).getCostMicros().longValue());
        assertEquals(113960000L, updated.get(211560036921L).getCostMicros().longValue());
        assertEquals(63300000L, updated.get(211560037089L).getCostMicros().longValue());
        assertEquals(7600000L, updated.get(211560036924L).getCostMicros().longValue());
    }

    private List<GoogleExpensesRow> loadGoogleExpenseRowFulls(String fileName) {
        List<GoogleExpensesRow> result = new ArrayList<>();

        try (
                BufferedReader reader =
                        new BufferedReader(new InputStreamReader(this.getClass().getResourceAsStream("test_data/" + fileName)))
        ) {
            String line;
            while ((line = reader.readLine()) != null) {
                result.add(GoogleExpensesRow.from(line));
            }
        } catch (Exception e) {
            throw new RuntimeException(e);
        }

        return result;
    }
}
