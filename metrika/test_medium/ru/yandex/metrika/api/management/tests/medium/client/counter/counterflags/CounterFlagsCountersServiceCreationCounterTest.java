package ru.yandex.metrika.api.management.tests.medium.client.counter.counterflags;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;

import ru.yandex.metrika.api.management.config.CountersServiceConfig;

import static org.junit.Assert.assertEquals;
import static ru.yandex.metrika.CommonTestsHelper.FAKE_USER;

@RunWith(Parameterized.class)
@ContextConfiguration
public class CounterFlagsCountersServiceCreationCounterTest extends AbstractCounterFlagsCountersServiceTest {

    @Test
    public void testUseInBenchmarks() {
        var created = createCounterWithFlags(counterFlags);
        var returned = countersService.getById(FAKE_USER, FAKE_USER, created.getId(), fields);
        assertEquals(expected.useInBenchmarks(), returned.getCounterFlags().useInBenchmarks());
    }

    @Test
    public void testIncognito() {
        var created = createCounterWithFlags(counterFlags);
        var returned = countersService.getById(FAKE_USER, FAKE_USER, created.getId(), fields);
        assertEquals(expected.incognito(), returned.getCounterFlags().incognito());
    }

    @Test
    public void testStatisticsOverSite() {
        var created = createCounterWithFlags(counterFlags);
        var returned = countersService.getById(FAKE_USER, FAKE_USER, created.getId(), fields);
        assertEquals(expected.statisticsOverSite(), returned.getCounterFlags().statisticsOverSite());
    }

    @Test
    public void testNewsEnabledByUser() {
        var created = createCounterWithFlags(counterFlags);
        var returned = countersService.getById(FAKE_USER, FAKE_USER, created.getId(), fields);
        assertEquals(expected.newsEnabledByUser(), returned.getCounterFlags().newsEnabledByUser());
    }

    @Test
    public void testNewsEnabledByClassifier() {
        var created = createCounterWithFlags(counterFlags);
        var returned = countersService.getById(FAKE_USER, FAKE_USER, created.getId(), fields);
        assertEquals(false, returned.getCounterFlags().newsEnabledByClassifier());
    }

    @Configuration
    @Import({CountersServiceConfig.class})
    public static class Config {}
}
