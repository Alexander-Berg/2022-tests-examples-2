package ru.yandex.metrika.schedulerd.cron.task.monitoringd;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.Set;
import java.util.stream.IntStream;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.schedulerd.cron.task.monitoringd.v2.MonitoringBaseTest;

import static org.junit.Assert.assertEquals;

public class DomainCountersDaoTest extends MonitoringBaseTest {
    private static final int CHECK_COUNT = 30;
    private static final int PAIRS_COUNT = CHECK_COUNT * 10;
    private static final String TABLE = "domain_counters";

    Random random = new Random();
    DomainCountersDao dao;
    Map<String, Set<Integer>> generatedDomainCounterMap;

    private void generateDomainCounterMap(int count) {
        generatedDomainCounterMap = new HashMap<>();
        List<Object[]> pairs = new ArrayList<>();
        IntStream
                .range(0, count)
                .forEach(value -> {
                    String domain = C_DOMAINS[random.nextInt(C_DOMAINS.length)];
                    int cId = C_IDS[random.nextInt(C_IDS.length)];
                    pairs.add(new Object[]{domain, cId});
                    generatedDomainCounterMap.computeIfAbsent(domain, k -> new HashSet<>()).add(cId);
                });
        countersTemplate.batchUpdate("" +
                        "INSERT IGNORE INTO " + TABLE + "(domain, counter_id) VALUES (?,?)",
                pairs
        );
    }

    @Before
    public void setUp() throws Exception {
        super.setUp();
        stepsMon.cleanCounters(TABLE);
        dao = new DomainCountersDao();
        dao.setJdbcTemplate(countersTemplate);
        generateDomainCounterMap(PAIRS_COUNT);
    }

    @After
    public void tearDown() throws Exception {
        stepsMon.cleanCounters(TABLE);
        dao = null;
        super.tearDown();
    }

    @Test
    public void getDomainToCountersMap() {
        Set<String> domains = new HashSet<>();
        Map<String, Set<Integer>> expected = new HashMap<>();

        IntStream.range(0, CHECK_COUNT).forEach(value -> domains.add(C_DOMAINS[random.nextInt(C_DOMAINS.length)]));
        domains.forEach(domain -> expected.put(domain, generatedDomainCounterMap.get(domain)));

        Map<String, Set<Integer>> resultSet = dao.getDomainToCountersMap(domains);

        assertEquals(expected, resultSet);
    }
}
