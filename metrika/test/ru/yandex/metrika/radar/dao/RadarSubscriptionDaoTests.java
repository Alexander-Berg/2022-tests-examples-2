package ru.yandex.metrika.radar.dao;

import java.util.Arrays;
import java.util.List;

import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.radar.address.Address;
import ru.yandex.metrika.radar.address.Edge;
import ru.yandex.metrika.radar.address.FullAddress;
import ru.yandex.metrika.radar.address.IntEdge;
import ru.yandex.metrika.radar.address.StringEdge;
import ru.yandex.metrika.radar.segments.DimensionId;

/**
 * @author lemmsh
 * @since 7/2/13
 */

public class RadarSubscriptionDaoTests {

    private FullAddress prepareFullAddress(){
        List<Edge> edges1 = Arrays.<Edge>asList(new StringEdge(1, "o1"), new StringEdge(1, "o2"));
        List<Edge> edges2 = Arrays.<Edge>asList(new StringEdge(2, "a1"),
            new StringEdge(2, "a2"),
            new StringEdge(2, "a3"));
        return FullAddress.builder()
            .append(DimensionId.TRAFFIC_SOURCE, new Address(edges1))
            .append(DimensionId.START_PAGE, new Address(edges2))
            .get();
    }

    private FullAddress prepareTranslatableFullAddress(){
        List<Edge> edges1 = Arrays.<Edge>asList(new StringEdge(1, "o1"), new StringEdge(1, "o2"));
        return FullAddress.builder()
            .append(DimensionId.START_PAGE, new Address(edges1))
            .get();
    }


    private FullAddress prepareAnotherFullAddress(){
        return FullAddress.builder()
            .append(1, new Address(new IntEdge(1, 1), new StringEdge(2, "szzx")))
            .append(2, new Address(new IntEdge(2, 3), new StringEdge(2, "szzx")))
            .get();
    }

    @Test
    @Ignore
    public void testRadarSubscriptionDao() throws Exception {
        //RadarSubscriptionDaoImpl RadarSubscriptionDao = new RadarSubscriptionDaoImpl();
        //RadarSubscriptionDao.setJdbcTemplate(GrepLog2.getTemplate("localhost", 3308, "root", "qwerty", "conv_main"));
        //RadarSubscriptionDao.afterPropertiesSet();
        //RadarSubscriptionDao.updateFullAddress(2, prepareAnotherFullAddress());
        //RadarSubscriptionDao.removeSubscription(1);
        //RadarSubscriptionDao.removeSubscription(3);
        //RadarSubscriptionDao.saveFullAddress(1,prepareTranslatableFullAddress());
        //System.out.println(RadarSubscriptionDao.listFullAddresses(1));



    }
}
