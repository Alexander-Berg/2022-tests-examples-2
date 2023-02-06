package ru.yandex.metrika.managers;

import org.apache.logging.log4j.Level;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.util.log.Log4jSetup;

/**
 * ssh -L 18090:mtrage05g:8090 mtweb02t
 * @author jkee
 */

@Ignore
public class VisitsCounterCachedTest {
    @Test
    public void testName() throws Exception {
        Log4jSetup.basicSetup(Level.DEBUG);
//        Router<MetrageDao> metrageRouter = Mockito.mock(Router.class);
//        MetrageTemplateImpl metrageTemplate = new MetrageTemplateImpl("http://localhost:18090");
//        metrageTemplate.afterPropertiesSet();
//        MetrageDaoImpl metrageDao = new MetrageDaoImpl(metrageTemplate);
//        Mockito.when(metrageRouter.getRouteForCounter(Mockito.anyInt())).thenReturn(metrageDao);
        VisitsCounterCachedImpl visitsCounterCached = new VisitsCounterCachedImpl();
//        visitsCounterCached.setMetrageDaoRouter(metrageRouter);
        System.out.println(visitsCounterCached.getData(101024, "2013-01-01", "2013-01-31").getVisits());
        System.out.println(visitsCounterCached.getData(101024, "2013-01-01", "2013-01-31").getHits());

        //Map<LocalDate, VisitsCounterCached.CounterData> byDate = visitsCounterCached.getByDate(501087, "2013-01-01", "2013-01-03");
        //System.out.println(byDate);

        //System.out.println(visitsCounterCached.getByDate(101024, "2013-01-02", "2013-01-04"));
        //System.out.println(visitsCounterCached.getByDate(101024, "2013-01-02", "2013-01-05"));
    }
}
