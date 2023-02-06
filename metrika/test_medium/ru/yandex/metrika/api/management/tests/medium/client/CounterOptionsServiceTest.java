package ru.yandex.metrika.api.management.tests.medium.client;

import java.sql.Timestamp;
import java.util.List;
import java.util.Map;

import org.joda.time.DateTime;
import org.junit.Assert;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.metrika.api.management.client.CounterLimits;
import ru.yandex.metrika.api.management.client.counter.CounterOptions;
import ru.yandex.metrika.api.management.client.counter.CounterOptionsService;
import ru.yandex.metrika.api.management.client.external.OfflineOptions;
import ru.yandex.metrika.api.management.client.external.PublisherOptions;
import ru.yandex.metrika.api.management.client.external.PublisherSchema;
import ru.yandex.metrika.api.management.config.CounterOptionsServiceConfig;
import ru.yandex.metrika.dbclients.MySqlTestSetup;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.util.collections.F;

@RunWith(SpringRunner.class)
@ContextConfiguration
public class CounterOptionsServiceTest {

    @Autowired
    public CounterOptionsService counterOptionsService;

    @Autowired
    private MySqlJdbcTemplate convMainTemplate;

    @BeforeClass
    public static void beforeClass() throws Exception {
        MySqlTestSetup.globalSetup();
    }

    @Before
    public void initData() {
        CounterOptions counterOptions20 = new CounterOptions(
            20,
            null, null, false, null,  false, false,
                false, null, null, false,
                false, null, false,
                null, false, false,
                false,
                0, 0, 0, 0,  0, 0,
            false, false, true, false, false
        );

        CounterOptions counterOptions22 = new CounterOptions(
                22,
                null, null, false, null,  false, false,
                false, null, null, false,
                false, null, false,
                null, false, false,
                false,
                0, 0, 0, 0, 0, 0,
                false, false, true, false, false
        );

        CounterOptions counterOptions24 = new CounterOptions(
                24,
                null, null, false, null, false, false,
                false, null,"microdata", true,
                true, new Timestamp(System.currentTimeMillis()), true,
                new Timestamp(System.currentTimeMillis()), true, false,
                false,
                0, 0, 0, 0, 0, 0,
                false, false, true, false, false
        );

        CounterOptions counterOptions26 = new CounterOptions(
                26,
                null, null, false, null, false,
                false, false, null,"json_ld", true,
                true, new Timestamp(System.currentTimeMillis()), true,
                new Timestamp(System.currentTimeMillis()), true, false,
                false,
                0, 0, 0, 0, 0, 0,
                false, false, true, false, false
        );

        CounterOptions counterOptions28 = new CounterOptions(
                28,
                null, null, false, null, false,
                false, false, null, null, false,
                false, null, false,
                null, false, false,
                false,
                0, 0, 0, 0, 0, 0,
                false, false, true, false, false
        );

        CounterOptions counterOptions30 = new CounterOptions(
                30,
                null, null, false, null, false,
                false, false, null,  null,false,
                false, null, false,
                null, false, false,
                false,
                1000, 100, 10, 10,5, 2,
                false, false, true, false, false
        );

        insertIntoCounterOptions(counterOptions20);
        insertIntoCounterOptions(counterOptions22);
        insertIntoCounterOptions(counterOptions24);
        insertIntoCounterOptions(counterOptions26);
        insertIntoCounterOptions(counterOptions28);
        insertIntoCounterOptions(counterOptions30);
    }

    @Test
    public void getAutogoalsEnabledMethodTest() {
        counterOptionsService.saveAutogoalsEnabled(24, true);

        List<Integer> counterIds = List.of(24, 25);
        Map<Integer, Boolean> autogoalsEnabledMap = counterOptionsService.getAutogoalsEnabled(counterIds);

        Assert.assertTrue(autogoalsEnabledMap.containsKey(24));
        Assert.assertTrue(autogoalsEnabledMap.containsKey(25));

        Assert.assertEquals(true, autogoalsEnabledMap.get(24));
        Assert.assertEquals(false, autogoalsEnabledMap.get(25));
    }

    @Test
    public void getPublisherOptionsMethodTest() {
        PublisherOptions publisherOptions = counterOptionsService.getPublisherOptions(24);
        Assert.assertNotNull(publisherOptions);

        Assert.assertEquals(true, publisherOptions.getEnabled());
        Assert.assertEquals(PublisherSchema.microdata, publisherOptions.getSchema());
    }

    @Test
    public void getPublisherOptionsMapMethodTest() {
        List<Integer> counterIds = List.of(24, 25);
        Map<Integer, PublisherOptions> publisherOptionsMap = counterOptionsService.getPublisherOptionsMap(counterIds);

        Assert.assertTrue(publisherOptionsMap.containsKey(24));
        Assert.assertTrue(publisherOptionsMap.containsKey(25));

        PublisherOptions publisherOptions24 = publisherOptionsMap.get(24);
        Assert.assertEquals(true, publisherOptions24.getEnabled());
        Assert.assertEquals(PublisherSchema.microdata, publisherOptions24.getSchema());

        PublisherOptions publisherOptions25 = publisherOptionsMap.get(25);
        Assert.assertEquals(false, publisherOptions25.getEnabled());
        Assert.assertNull(publisherOptions25.getSchema());
    }

    @Test
    public void updatePublisherOptionsMethodTest() {
        PublisherOptions publisherOptions = new PublisherOptions();
        publisherOptions.setEnabled(false);
        publisherOptions.setSchema(PublisherSchema.opengraph);
        counterOptionsService.updatePublisherOptions(26, publisherOptions);

        PublisherOptions actualPublisherOptions = getPublisherOptions(26);

        Assert.assertNotNull(actualPublisherOptions);
        Assert.assertEquals(false, actualPublisherOptions.getEnabled());
        Assert.assertEquals(PublisherSchema.opengraph, actualPublisherOptions.getSchema());
    }

    @Test
    public void getOfflineOptionsMethodTest() {
        OfflineOptions offlineOptions24 = counterOptionsService.getOfflineOptions(24);

        Assert.assertNotNull(offlineOptions24);
        Assert.assertEquals(true, offlineOptions24.getOfflineConversionExtendedThreshold());
        Assert.assertEquals(true, offlineOptions24.getOfflineCallsExtendedThreshold());
        Assert.assertEquals(true, offlineOptions24.getOfflineVisitsExtendedThreshold());
        Assert.assertNotNull(offlineOptions24.getOfflineCallsExtendedThresholdEnabledTime());
        Assert.assertNotNull(offlineOptions24.getOfflineConversionExtendedThresholdEnabledTime());

        OfflineOptions offlineOptions25 = counterOptionsService.getOfflineOptions(25);

        Assert.assertNotNull(offlineOptions25);
        Assert.assertEquals(false, offlineOptions25.getOfflineConversionExtendedThreshold());
        Assert.assertEquals(false, offlineOptions25.getOfflineCallsExtendedThreshold());
        Assert.assertEquals(false, offlineOptions25.getOfflineVisitsExtendedThreshold());
        Assert.assertNull(offlineOptions25.getOfflineCallsExtendedThresholdEnabledTime());
        Assert.assertNull(offlineOptions25.getOfflineConversionExtendedThresholdEnabledTime());
    }

    @Test
    public void getOfflineOptionsMapTest() {
        List<Integer> counterIds = List.of(24, 25);
        Map<Integer, OfflineOptions> offlineOptionsMap = counterOptionsService.getOfflineOptionsMap(counterIds);

        Assert.assertTrue(offlineOptionsMap.containsKey(24));
        Assert.assertTrue(offlineOptionsMap.containsKey(25));

        OfflineOptions offlineOptions24 = offlineOptionsMap.get(24);
        Assert.assertEquals(true, offlineOptions24.getOfflineConversionExtendedThreshold());
        Assert.assertEquals(true, offlineOptions24.getOfflineCallsExtendedThreshold());
        Assert.assertEquals(true, offlineOptions24.getOfflineVisitsExtendedThreshold());
        Assert.assertNotNull(offlineOptions24.getOfflineConversionExtendedThresholdEnabledTime());
        Assert.assertNotNull(offlineOptions24.getOfflineCallsExtendedThresholdEnabledTime());

        OfflineOptions offlineOptions25 = offlineOptionsMap.get(25);
        Assert.assertEquals(false, offlineOptions25.getOfflineConversionExtendedThreshold());
        Assert.assertEquals(false, offlineOptions25.getOfflineCallsExtendedThreshold());
        Assert.assertEquals(false, offlineOptions25.getOfflineVisitsExtendedThreshold());
        Assert.assertNull(offlineOptions25.getOfflineConversionExtendedThresholdEnabledTime());
        Assert.assertNull(offlineOptions25.getOfflineCallsExtendedThresholdEnabledTime());
    }

    @Test
    public void updateOfflineOptionsMethodTest() {
        OfflineOptions offlineOptions = new OfflineOptions();
        offlineOptions.setOfflineConversionExtendedThreshold(true);
        offlineOptions.setOfflineCallsExtendedThreshold(true);
        offlineOptions.setOfflineVisitsExtendedThreshold(true);
        offlineOptions.setOfflineConversionExtendedThresholdEnabledTime(DateTime.now());
        offlineOptions.setOfflineCallsExtendedThresholdEnabledTime(DateTime.now());

        counterOptionsService.updateOfflineOptions(28, offlineOptions);

        OfflineOptions actualOfflineOptions = getOfflineOptions(28);

        Assert.assertNotNull(actualOfflineOptions);
        Assert.assertEquals(true, actualOfflineOptions.getOfflineConversionExtendedThreshold());
        Assert.assertEquals(true, actualOfflineOptions.getOfflineCallsExtendedThreshold());
        Assert.assertEquals(true, actualOfflineOptions.getOfflineVisitsExtendedThreshold());
        Assert.assertNotNull(actualOfflineOptions.getOfflineConversionExtendedThresholdEnabledTime());
        Assert.assertNotNull(actualOfflineOptions.getOfflineCallsExtendedThresholdEnabledTime());
    }

    @Test
    public void saveAlternativeCdnMethodTest() {
        Assert.assertEquals(false, getAlternativeCdn(28));

        counterOptionsService.saveAlternativeCdn(28, true);
        Assert.assertEquals(true, getAlternativeCdn(28));
    }

    @Test
    public void getCounterLimitsMethodTest() {
        CounterLimits counterLimits = counterOptionsService.getCounterLimits(30);

        Assert.assertNotNull(counterLimits);
        Assert.assertEquals(1000, counterLimits.getMaxGoals());
        Assert.assertEquals(100, counterLimits.getMaxConditions());
        Assert.assertEquals(10, counterLimits.getMaxFilters());
        Assert.assertEquals(500, counterLimits.getSegmentLimits().maxApiSegments());
        Assert.assertEquals(500, counterLimits.getSegmentLimits().maxInterfaceSegments());
        Assert.assertEquals(50000, counterLimits.getMaxGeoPoints());
    }

    @Test
    public void turnOnFormGoalsMethodTest() {
        List<Integer> formGoalsEnabledCounterIdsBefore = getFormGoalsEnabledCounterIds(List.of(24, 26, 28));
        Assert.assertEquals(0, formGoalsEnabledCounterIdsBefore.size());

        counterOptionsService.turnOnFormGoals(List.of(24, 26));

        List<Integer> formGoalsEnabledCounterIds = getFormGoalsEnabledCounterIds(List.of(24, 26, 28));
        Assert.assertEquals(2, formGoalsEnabledCounterIds.size());

        List<Integer> expectedCounterIds = List.of(24, 26);
        Assert.assertTrue(expectedCounterIds.size() == formGoalsEnabledCounterIds.size() && expectedCounterIds.containsAll(formGoalsEnabledCounterIds) && formGoalsEnabledCounterIds.containsAll(expectedCounterIds));
    }

    @Test
    public void turnOnButtonGoalsMethodTest() {
        List<Integer> buttonGoalsEnabledCounterIdsBefore = getFormGoalsEnabledCounterIds(List.of(24, 26, 28));
        Assert.assertEquals(0, buttonGoalsEnabledCounterIdsBefore.size());

        counterOptionsService.turnOnButtonGoals(List.of(24, 26));

        List<Integer> buttonGoalsEnabledCounterIds = getButtonGoalsEnabledCounterIds(List.of(24, 26, 28));
        Assert.assertEquals(2, buttonGoalsEnabledCounterIds.size());

        List<Integer> expectedCounterIds = List.of(24, 26);
        Assert.assertTrue(expectedCounterIds.size() == buttonGoalsEnabledCounterIds.size() && expectedCounterIds.containsAll(buttonGoalsEnabledCounterIds) && buttonGoalsEnabledCounterIds.containsAll(expectedCounterIds));
    }

    private PublisherOptions getPublisherOptions(int counterId) {
        return new PublisherOptions(getCounterOptions(counterId));
    }

    private OfflineOptions getOfflineOptions(int counterId) {
        return new OfflineOptions(getCounterOptions(counterId));
    }

    private CounterOptions getCounterOptions(int counterId) {
        return convMainTemplate.queryForObject(
                "SELECT * FROM `counter_options` where counter_id = ?",
                CounterOptions.MAPPER,
                counterId
        );
    }

    private Boolean getAlternativeCdn(int counterId) {
        return convMainTemplate.queryForObject(
                "SELECT alternative_cdn FROM counter_options where counter_id = ?",
                Boolean.class,
                counterId
        );
    }

    private List<Integer> getFormGoalsEnabledCounterIds(List<Integer> counterIds) {
        return convMainTemplate.queryForList(
                "select counter_id from counter_options where counter_id in (" + F.join(counterIds, ",") + ") and form_goals=1",
                Integer.class);
    }

    private List<Integer> getButtonGoalsEnabledCounterIds(List<Integer> counterIds) {
        return convMainTemplate.queryForList(
                "select counter_id from counter_options where counter_id in (" + F.join(counterIds, ",") + ") and button_goals=1",
                Integer.class);
    }

    private void insertIntoCounterOptions(CounterOptions counterOptions) {
        convMainTemplate.update("INSERT IGNORE INTO counter_options(" +
                "counter_id, " +
                "publisher_enabled, " +
                "publisher_schema, " +
                "offline_conv_extended_threshold," +
                "offline_calls_extended_threshold," +
                "offline_visits_extended_threshold," +
                "offline_conv_extended_threshold_enabled_time," +
                "offline_calls_extended_threshold_enabled_time," +
                "alternative_cdn," +
                "max_goals," +
                "max_conditions," +
                "max_operations," +
                "max_filters," +
                "max_api_segments," +
                "max_interface_segments) " +
                "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                counterOptions.counterId(),
                counterOptions.publisherEnabled(),
                counterOptions.publisherSchema(),
                counterOptions.offlineConvExtendedThreshold(),
                counterOptions.offlineCallsExtendedThreshold(),
                counterOptions.offlineVisitsExtendedThreshold(),
                counterOptions.offlineConvExtendedThresholdEnabledTime(),
                counterOptions.offlineCallsExtendedThresholdEnabledTime(),
                counterOptions.alternativeCdn(),
                counterOptions.maxGoals(),
                counterOptions.maxConditions(),
                counterOptions.maxOperations(),
                counterOptions.maxFilters(),
                counterOptions.maxApiSegments(),
                counterOptions.maxInterfaceSegments()
        );
    }

    @Configuration
    @Import(CounterOptionsServiceConfig.class)
    public static class Config {}
}
