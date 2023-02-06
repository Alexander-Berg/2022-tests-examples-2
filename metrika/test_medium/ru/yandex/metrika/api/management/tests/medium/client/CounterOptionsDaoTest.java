package ru.yandex.metrika.api.management.tests.medium.client;

import java.sql.Timestamp;
import java.util.List;

import org.junit.Assert;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.ExpectedException;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.metrika.api.management.client.counter.CounterOptions;
import ru.yandex.metrika.api.management.client.counter.CounterOptionsDao;
import ru.yandex.metrika.api.management.client.external.PublisherOptions;
import ru.yandex.metrika.api.management.client.external.PublisherSchema;
import ru.yandex.metrika.api.management.config.CounterOptionsDaoConfig;
import ru.yandex.metrika.dbclients.MySqlTestSetup;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;

@RunWith(SpringRunner.class)
@ContextConfiguration
public class CounterOptionsDaoTest {

    @Autowired
    private CounterOptionsDao counterOptionsDao;

    @Autowired
    private MySqlJdbcTemplate convMainTemplate;

    @Rule
    public ExpectedException exception = ExpectedException.none();

    @BeforeClass
    public static void beforeClass() throws Exception {
        MySqlTestSetup.globalSetup();
    }

    @Before
    public void initData() {
        CounterOptions counterOptions20 = new CounterOptions(
                20,
                null, null, false, null, false, false,
                false, null, null, false,
                false, null, false,
                null, false, false,
                false,
                0, 0, 0, 0,  0, 0,
                false, false, true, false, false
        );

        CounterOptions counterOptions22 = new CounterOptions(
                22,
                null, null, false, null, false, false,
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
                null, null, false, null,  false, false,
                false, null,"json_ld", true,
                true, new Timestamp(System.currentTimeMillis()), true,
                new Timestamp(System.currentTimeMillis()), true, false,
                false,
                0, 0, 0, 0,  0, 0,
                false, false, true, false, false
        );

        CounterOptions counterOptions28 = new CounterOptions(
                28,
                null, null, false, null, false, false,
                false, null, null, false,
                false, null, false,
                null, false, false,
                false,
                0, 0, 0, 0,  0, 0,
                false, false, true, false, false
        );

        CounterOptions counterOptions30 = new CounterOptions(
                30,
                null, null, false, null,  false, false,
                false, null,  null,false,
                false, null, false,
                null, false, false,
                false,
                1000, 100, 10, 10, 5, 2,
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
    public void getCounterOptionsMethodTest() {
        CounterOptions counterOptionsWithCounterId20 = counterOptionsDao.getCounterOptions(20);
        Assert.assertNotNull(counterOptionsWithCounterId20);
        Assert.assertEquals(20, counterOptionsWithCounterId20.counterId());

        Assert.assertNull(counterOptionsDao.getCounterOptions(21));
    }

    @Test
    public void getCounterOptionsListMethodTest() {
        List<Integer> counterIds = List.of(20, 21, 22);

        List<CounterOptions> counterOptions = counterOptionsDao.getCounterOptionsList(counterIds);

        Assert.assertEquals(2, counterOptions.size());
        List<Integer> counterOptionsCounterIds = counterOptions.stream()
                .map(CounterOptions::counterId).toList();
        Assert.assertTrue(counterOptionsCounterIds.contains(20));
        Assert.assertTrue(counterOptionsCounterIds.contains(22));
    }

    @Test
    public void turnOnButtonGoalsMethodTest() {
        List<Integer> counterIds = List.of(20, 22);

        List<CounterOptions> counterOptionsList = counterOptionsDao.getCounterOptionsList(counterIds);

        Assert.assertEquals(2, counterOptionsList.size());
        for (CounterOptions counterOptions: counterOptionsList) {
            Assert.assertFalse(counterOptions.buttonGoals());
        }

        counterOptionsDao.turnOnButtonGoals(List.of(20));

        List<CounterOptions> counterOptionsWithButtonGoalsTrue = counterOptionsDao.getCounterOptionsList(List.of(20));
        List<CounterOptions> counterOptionsWithButtonGoalsFalse = counterOptionsDao.getCounterOptionsList(List.of(22));
        Assert.assertEquals(1, counterOptionsWithButtonGoalsTrue.size());
        Assert.assertEquals(1, counterOptionsWithButtonGoalsFalse.size());
        for (CounterOptions counterOptions: counterOptionsWithButtonGoalsTrue) {
            Assert.assertTrue(counterOptions.buttonGoals());
        }
        for (CounterOptions counterOptions: counterOptionsWithButtonGoalsFalse) {
            Assert.assertFalse(counterOptions.buttonGoals());
        }
    }

    @Test
    public void turnOnFormGoalsMethodTest() {
        List<Integer> counterIds = List.of(20, 22);

        List<CounterOptions> counterOptionsList = counterOptionsDao.getCounterOptionsList(counterIds);
        Assert.assertEquals(2, counterOptionsList.size());
        for (CounterOptions counterOptions: counterOptionsList) {
            Assert.assertFalse(counterOptions.formGoals());
        }

        counterOptionsDao.turnOnFormGoals(List.of(22));

        List<CounterOptions> counterOptionsWithFormGoalsTrue = counterOptionsDao.getCounterOptionsList(List.of(22));
        List<CounterOptions> counterOptionsWithFormGoalsFalse = counterOptionsDao.getCounterOptionsList(List.of(20));
        Assert.assertEquals(1, counterOptionsWithFormGoalsTrue.size());
        Assert.assertEquals(1, counterOptionsWithFormGoalsFalse.size());
        for (CounterOptions counterOptions: counterOptionsWithFormGoalsTrue) {
            Assert.assertTrue(counterOptions.formGoals());
        }
        for (CounterOptions counterOptions: counterOptionsWithFormGoalsFalse) {
            Assert.assertFalse(counterOptions.formGoals());
        }
    }

    @Test
    public void saveAutogoalsEnabledMethodTest() {
        List<Integer> counterIds = List.of(20);
        List<CounterOptions> counterOptionsList = counterOptionsDao.getCounterOptionsList(counterIds);
        Assert.assertEquals(1, counterOptionsList.size());

        CounterOptions counterOptions = counterOptionsList.get(0);

        Assert.assertEquals(20, counterOptions.counterId());
        Assert.assertFalse(counterOptions.autogoalsEnabled());

        counterOptionsDao.saveAutogoalsEnabled(counterOptions.counterId(), true);

        CounterOptions counterOptionsWithAutogoalsEnabledTrue = counterOptionsDao.getCounterOptionsList(counterIds).get(0);

        Assert.assertEquals(20, counterOptionsWithAutogoalsEnabledTrue.counterId());
        Assert.assertTrue(counterOptionsWithAutogoalsEnabledTrue.autogoalsEnabled());
    }

    @Test
    public void updatePublisherOptionsMethodTest() {
        PublisherOptions publisherOptions = new PublisherOptions();

        publisherOptions.setEnabled(true);
        publisherOptions.setSchema(PublisherSchema.json_ld);

        counterOptionsDao.updatePublisherOptions(20, publisherOptions);
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
    @Import(CounterOptionsDaoConfig.class)
    public static class Config {}
}
