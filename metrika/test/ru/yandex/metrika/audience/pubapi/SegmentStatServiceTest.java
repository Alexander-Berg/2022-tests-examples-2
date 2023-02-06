package ru.yandex.metrika.audience.pubapi;

import java.util.LinkedHashMap;
import java.util.stream.Collectors;

import org.apache.commons.lang3.tuple.Pair;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.dbclients.clickhouse.HttpTemplate;
import ru.yandex.metrika.tool.AllDatabases;

/**
 * Created by orantius on 05.07.16.
 */
@Ignore
public class SegmentStatServiceTest {

    @Test
    public void getStat() throws Exception {
        String sql = "select regionToName(regionToCity(Region)) as City, uniqExact(UserID) as users from segment_joined_54564 where City != '' group by City order by users desc";
        // ssh -L 8890:localhost:8123 mtaudi01gt.mtrs.yandex.ru
        HttpTemplate httpTemplate = AllDatabases.getCHTemplate("localhost", 8890, "audience_visitors_storage");
        LinkedHashMap<String, Double> collect = httpTemplate.query(sql, (rs, rowNum) -> Pair.of(rs.getString("City"), rs.getDouble("users"))).stream()
                .collect(Collectors.toMap(p -> p.getLeft(), p -> p.getRight(), (u,v)-> Math.max(u,v), LinkedHashMap::new));
        System.out.println("collect = " + collect);
    }

}
