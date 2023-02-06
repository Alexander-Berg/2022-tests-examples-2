package ru.yandex.metrika.schedulerd.cron.task.monitoringd.v2;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Random;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import org.joda.time.DateTime;
import org.junit.After;
import org.junit.Before;

import ru.yandex.metrika.api.monitoringd.MonStatus;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.schedulerd.tests.SchedulerdBaseTest;

public abstract class MonitoringBaseTest extends SchedulerdBaseTest {
    public static final Random RND = new Random();
    public static final int[] C_IDS = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15}; // Взято из дампа для conv_main
    public static final String[] C_DOMAINS = {
            "mysite1.ru", "mysite2.ru", "mysite3.ru", "mysite4.ru", "mysite5.ru",
            "mysite6.ru", "mysite7.ru", "mysite8.ru", "mysite9.ru", "mysite10.ru",
            "mysite11.ru", "mysite12.ru", "mysite13.ru", "mysite14.ru", "mysite15.ru"
    };
    protected static final String LB_TOPIC = "yabs-sb/url-monitoring-diffs";
    protected static final String LB_CONSUMER = "bs-url-monitoring";
    static final long NOW = DateTime.now().getMillis();
    static final MonStatus UNDEF = MonStatus.undef;
    static final MonStatus GOOD = MonStatus.alive;
    static final MonStatus BAD = MonStatus.dead;
    protected MySqlJdbcTemplate monitoringTemplate;
    protected MySqlJdbcTemplate countersTemplate;
    protected MonitoringSteps stepsMon;
    protected MonitoringLbSteps stepsLb;

    public static MonitoringState state(int counterId, MonStatus state, int t) {
        return new MonitoringState(
                "dump_message",
                state == MonStatus.alive ? 200 : 500,
                state,
                C_DOMAINS[counterId - 1],
                counterId,
                NOW - TimeUnit.MINUTES.toMillis(t)
        ) {
            @Override
            public String toString() {
                return counterId + "(" + state.toString() + ":" + t + ")";
            }
        };
    }

    @Before
    public void setUp() throws Exception {
        stepsMon = new MonitoringSteps(steps);
        stepsLb = new MonitoringLbSteps(
                LB_TOPIC,
                LB_CONSUMER,
                NOW,
                steps.getLogbrokerClientFactory()
        );
        monitoringTemplate = steps.getMonitoringTemplate();
        countersTemplate = steps.getCountersTemplate();
        fillCounterDomainTable();
        stepsLb.init(getLbTopicData());
    }

    @After
    public void tearDown() throws Exception {
        monitoringTemplate = null;
        countersTemplate = null;
        stepsMon.cleanCounters("domain_counters");
        stepsLb.cleanLbConsumer();
    }

    public List<byte[]> getLbTopicData() {
        return Collections.emptyList();
    }

    public void fillCounterDomainTable() {
        countersTemplate.batchUpdate(
                "INSERT IGNORE INTO domain_counters (counter_id, domain) VALUES (?,?)",
                IntStream.range(0, C_IDS.length).boxed().map(idx -> new Object[]{C_IDS[idx], C_DOMAINS[idx]}).collect(Collectors.toList())
        );
    }

    protected List<byte[]> generateLbMessages(int count, final Set<MonitoringState> localStates) {
        List<byte[]> result = new ArrayList<>();
        IntStream.range(0, count).forEach(idx -> {
            String url = C_DOMAINS[idx % C_IDS.length];
            int cId = C_IDS[idx % C_IDS.length];

            boolean isOk = RND.nextBoolean();
            localStates.add(state(
                    cId,
                    isOk ? GOOD : BAD,
                    idx
            ));

            result.add(stepsLb.lbStatus(url, isOk, idx));
        });
        return result;
    }
}
