package ru.yandex.metrika.api.management.tests.medium.client.counter.counterflags;

import java.lang.reflect.Field;
import java.util.List;

import com.google.common.cache.LoadingCache;
import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;

import ru.yandex.metrika.api.Feature;
import ru.yandex.metrika.api.constructor.contr.FeatureService;
import ru.yandex.metrika.api.management.client.counter.CounterFlagsService;
import ru.yandex.metrika.api.management.client.counter.CounterOptionsService;
import ru.yandex.metrika.api.management.config.CounterFlagsServiceConfig;
import ru.yandex.metrika.api.management.tests.util.FeatureServiceMock;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;


@RunWith(Parameterized.class)
@ContextConfiguration
public class CounterFlagsServiceTest extends AbstractCounterFlagsTest {

    @Autowired
    private CounterFlagsService counterFlagsService;

    @Autowired
    private CounterOptionsService counterOptionsService;

    @Autowired
    private FeatureService featureService;

    @Autowired
    @Qualifier("convMainTemplate")
    MySqlJdbcTemplate convMainTemplate;

    private static final int counterId = 26;


    @Parameterized.Parameters(name = "{0}")
    public static List<Object[]> getAllCounterFlagsVariationsWithExpectedUploadingsResults() {
        return getAllCounterFlagsVariationsWithExpectedUploadingsResults(counterId);
    }

    @Test
    public void test() throws NoSuchFieldException, IllegalAccessException {
        setDefaultFlags();
        setPredefinedFlags();
        counterFlagsService.setFlagsForCounters(List.of(counterFlags));
        var result = counterFlagsService.getFlagsForCounters(List.of(counterId)).getOrDefault(counterId, null);
        Assert.assertEquals(expected, result);
    }

    private void setDefaultFlags() throws NoSuchFieldException, IllegalAccessException {
        convMainTemplate.update("UPDATE conv_main.counter_options" +
                " SET use_in_benchmarks = true, direct_allow_use_goals_without_access = false, news_enabled_by_user = false" +
                " WHERE counter_id = " + counterId);
        Field cacheToClean = counterOptionsService.getClass().getDeclaredField("counterOptionsLoadingCache");
        cacheToClean.setAccessible(true);
        ((LoadingCache<Integer, ?>) cacheToClean.get(counterOptionsService)).invalidateAll();
        convMainTemplate.update("UPDATE conv_main.code_options" +
                " SET incognito = 'disabled', collect_first_party_data = true, statistics_over_site = true" +
                " WHERE counter_id = " + counterId);
        if (featureService instanceof FeatureServiceMock featureServiceMock) {
            featureServiceMock.clear();
        }
    }

    private void setPredefinedFlags() {
        if (Boolean.TRUE.equals(counterFlags.newsEnabledByClassifier())) {
            featureService.addFeature(counterId, Feature.news_enabled_by_classifier);
        }
    }

    @Configuration
    @Import(CounterFlagsServiceConfig.class)
    public static class Config {}
}
