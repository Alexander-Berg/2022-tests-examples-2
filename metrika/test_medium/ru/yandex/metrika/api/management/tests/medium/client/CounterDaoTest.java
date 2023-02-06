package ru.yandex.metrika.api.management.tests.medium.client;

import java.util.List;

import org.jetbrains.annotations.Nullable;
import org.junit.Assert;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.metrika.api.management.client.counter.CountersDao;
import ru.yandex.metrika.api.management.client.external.CounterSource;
import ru.yandex.metrika.api.management.config.CountersDaoConfig;
import ru.yandex.metrika.dbclients.MySqlTestSetup;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.dbclients.mysql.RowMappers;

@RunWith(SpringRunner.class)
@ContextConfiguration
public class CounterDaoTest {

    @Autowired
    private CountersDao countersDao;

    @Autowired
    private MySqlJdbcTemplate convMainTemplate;

    @BeforeClass
    public static void beforeClass() throws Exception {
        MySqlTestSetup.globalSetup();
    }

    @Test
    public void makeCounterPartnerMethodTest() {
        int counterId = createCounterWithCertainCounterSource(null);

        countersDao.makeCounterPartner(counterId);

        CounterSource counterSource = getCounterSource(counterId);
        Assert.assertEquals(CounterSource.partner, counterSource);
    }

    @Test
    public void makeCounterSimpleMethodTest() {
        int counterId = createCounterWithCertainCounterSource(CounterSource.partner);

        countersDao.makeCounterSimple(counterId);

        CounterSource counterSource = getCounterSource(counterId);
        Assert.assertNull(counterSource);
    }

    private CounterSource getCounterSource(int id) {
        List<String> sources = convMainTemplate.query("SELECT source from counters where counter_id = " + id, RowMappers.STRING);

        if (sources.isEmpty()) {
            return null;
        }

        return CounterSource.fromVal(sources.get(0));
    }

    private int createCounterWithCertainCounterSource(@Nullable CounterSource counterSource) {
        return (int) convMainTemplate.updateRowGetGeneratedKey(
                "INSERT INTO counters " +
                        "(`name`," +
                        "create_time," +
                        "external_class," +
                        "external_cid," +
                        "email," +
                        "LayerID," +
                        "informer_color," +
                        "informer_indicators," +
                        "source) " +
                        "VALUES (?,NOW(),?,?,?,?,?,?,?)",
                "test",
                0,
                0,
                "test email",
                1,
                "test informer color",
                "test informer indicators",
                counterSource == null ? null : counterSource.toString()
        );
    }

    @Configuration
    @Import(CountersDaoConfig.class)
    public static class Config {}
}
