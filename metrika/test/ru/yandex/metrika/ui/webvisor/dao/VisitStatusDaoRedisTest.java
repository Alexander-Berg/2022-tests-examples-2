package ru.yandex.metrika.ui.webvisor.dao;

import java.time.LocalDate;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Date;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;

import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.dbclients.redis.RedisConnector;
import ru.yandex.metrika.dbclients.redis.RedisSourceList;
import ru.yandex.metrika.managers.VisitStatusDaoRedis;
import ru.yandex.metrika.util.log.Log4jSetup;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;

@Ignore
public class VisitStatusDaoRedisTest {

    RedisConnector connector;

    @Before
    public void setUp() {

        Log4jSetup.basicSetup();

        RedisSourceList sources = new RedisSourceList();
        sources.getSource().get(0).setHost("vla-zv2waq17dq6utpbf.db.yandex.net");
        sources.getSource().get(0).setPort(26379);
        sources.setPassword("");
        sources.setMasterId("metrika-quota-test");

        connector = new RedisConnector(sources);
        connector.init();
    }

    @Test
    public void testEmpty() {
        VisitStatusDaoRedis visitStatusDaoRedis = new VisitStatusDaoRedis(connector);

        List<Long> result1 = visitStatusDaoRedis.getSelectedVisits(2);
        assertEquals(result1, Collections.emptyList());

        List<Long> result2 = visitStatusDaoRedis.getViewedVisits(2);
        assertEquals(result2, Collections.emptyList());

        Date result3 = visitStatusDaoRedis.getAllViewedVisitsDate(2, 3);
        assertNull(result3);
    }

    @Test
    public void testDate() {
        VisitStatusDaoRedis visitStatusDaoRedis = new VisitStatusDaoRedis(connector);

        visitStatusDaoRedis.markAllViewed(1, 2);
        Date result1 = visitStatusDaoRedis.getAllViewedVisitsDate(1, 2);
        assertEquals(toLocalDate(result1), LocalDate.now());

        Date result2 = visitStatusDaoRedis.getAllViewedVisitsDate(1, 3);
        assertNull(result2);

        Date result3 = visitStatusDaoRedis.getAllViewedVisitsDate(2, 2);
        assertNull(result3);
    }

    @Test
    public void testViewed() {
        VisitStatusDaoRedis visitStatusDaoRedis = new VisitStatusDaoRedis(connector);

        visitStatusDaoRedis.markViewed(1, new long[]{1, 2, 3});

        List<Long> result1 = visitStatusDaoRedis.getViewedVisits(1);
        assertArrayEquals(result1.toArray(new Long[0]), new Long[]{1L,2L,3L});

        visitStatusDaoRedis.removeViewed(1, 3);
        List<Long> result2 = visitStatusDaoRedis.getViewedVisits(1);
        assertArrayEquals(result2.toArray(new Long[0]), new Long[]{1L,2L});

        visitStatusDaoRedis.markViewed(1, 2);
        List<Long> result3 = visitStatusDaoRedis.getViewedVisits(1);
        assertArrayEquals(result3.toArray(new Long[0]), new Long[]{1L,2L});

        visitStatusDaoRedis.markViewed(1, 4);
        List<Long> result4 = visitStatusDaoRedis.getViewedVisits(1);
        assertArrayEquals(result4.toArray(new Long[0]), new Long[]{1L,2L,4L});

        Set<Long> result5 = visitStatusDaoRedis.whichAreViewed(1, Arrays.asList(new Long[]{2L}));
        assertTrue(result5.contains(2L));
        assertEquals(1, result5.size());

        //no fall on non exists keys
        visitStatusDaoRedis.removeViewed(1000, 1);
        visitStatusDaoRedis.removeViewed(1, 1000);
    }

    @Test
    public void testSelected() {
        VisitStatusDaoRedis visitStatusDaoRedis = new VisitStatusDaoRedis(connector);

        visitStatusDaoRedis.markSelected(1, 1, "+1");
        visitStatusDaoRedis.markSelected(1, 2, "+2");
        visitStatusDaoRedis.markSelected(1, 3, "+3");

        List<Long> result1 = visitStatusDaoRedis.getSelectedVisits(1);
        assertArrayEquals(result1.toArray(new Long[0]), new Long[]{1L,2L,3L});

        visitStatusDaoRedis.removeSelected(1, 3);
        List<Long> result2 = visitStatusDaoRedis.getSelectedVisits(1);
        assertArrayEquals(result2.toArray(new Long[0]), new Long[]{1L,2L});


        visitStatusDaoRedis.markSelected(1, 4, "+4");
        List<Long> result3 = visitStatusDaoRedis.getSelectedVisits(1);
        assertArrayEquals(result3.toArray(new Long[0]), new Long[]{1L,2L,4L});


        Map<Long, Optional<String>> result4 = visitStatusDaoRedis.getSelectedVisitsWithText(1, new ArrayList<>(Arrays.asList(1L, 2L, 4L)));
        assertEquals(result4.get(1L).get(), "+1");
        assertEquals(result4.get(2L).get(), "+2");
        assertEquals(result4.get(4L).get(), "+4");

        Set<Long> result5 = visitStatusDaoRedis.whichAreSelected(1, Arrays.asList(new Long[]{2L}));
        assertTrue(result5.contains(2L));
        assertEquals(1, result5.size());

        //no fall on non exists keys
        visitStatusDaoRedis.removeSelected(1000, 1);
        visitStatusDaoRedis.removeSelected(1, 1000);
    }

    private LocalDate toLocalDate(Date dateToConvert) {
        return dateToConvert.toInstant()
                .atZone(ZoneId.systemDefault())
                .toLocalDate();
    }

}
