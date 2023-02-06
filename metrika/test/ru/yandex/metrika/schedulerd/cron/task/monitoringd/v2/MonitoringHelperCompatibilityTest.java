package ru.yandex.metrika.schedulerd.cron.task.monitoringd.v2;

import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ThreadLocalRandom;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.stream.Stream;

import org.junit.After;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.monitoring.logbroker.LogbrokerStatusChange;
import ru.yandex.metrika.schedulerd.cron.task.monitoringd.BSMonitoringHelper;
import ru.yandex.metrika.schedulerd.cron.task.monitoringd.DomainCountersDao;

public class MonitoringHelperCompatibilityTest {
    private static final int COUNTERS_COUNT = 2000;
    private static final int DOMAINS_COUNT = 200;
    private static final int COUNTER_PER_DOMAIN = 10;
    private static final int BATCH_SIZE = 10;
    private static final int TOTAL_RECORD = 1000;

    TestHelper helper = new TestHelper();

    private final List<Long> counters = IntStream
            .range(0, COUNTERS_COUNT)
            .mapToObj(value -> helper.getRndCounterId(7))
            .collect(Collectors.toList());

    private final List<String> domains = IntStream
            .range(0, DOMAINS_COUNT)
            .mapToObj(value -> helper.getNextDomain())
            .collect(Collectors.toList());


    private final Map<String, Set<Integer>> domainCountersMap = domains
            .stream()
            .map(domain -> {
                Set<Integer> counters = helper.getRandomSubset(
                        this.counters.stream().mapToInt(Long::intValue).boxed().collect(Collectors.toList()),
                        ThreadLocalRandom.current().nextInt(COUNTER_PER_DOMAIN)
                );
                return Map.entry(domain, counters);
            })
            .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));


    private MonitoringHelper monitoringHelper;
    private BSMonitoringHelper bsMonitoringHelper;

    @Before
    public void setUp() throws Exception {
        DomainCountersDao domainCountersDaoMock = new DomainCountersDaoMock(domainCountersMap);
        this.monitoringHelper = new MonitoringHelper(domainCountersDaoMock);
        this.monitoringHelper.setBatchSize(BATCH_SIZE);
        this.bsMonitoringHelper = new BSMonitoringHelper(domainCountersDaoMock);
        this.bsMonitoringHelper.setBatchSize(BATCH_SIZE);
    }

    @After
    public void tearDown() throws Exception {
        this.monitoringHelper = null;
        this.bsMonitoringHelper = null;
    }

    @Test
    public void transform() {
        List<LogbrokerStatusChange> statusChanges = helper.generateStatusChanges(domains, TOTAL_RECORD);
        Stream<MonitoringState> oldNotifications = bsMonitoringHelper.transformToStream(statusChanges);
        Stream<MonitoringState> newNotifications = monitoringHelper.transform(statusChanges.stream());
        Assert.assertEquals(
                oldNotifications.collect(Collectors.toList()),
                newNotifications.collect(Collectors.toList())
        );
    }

}
