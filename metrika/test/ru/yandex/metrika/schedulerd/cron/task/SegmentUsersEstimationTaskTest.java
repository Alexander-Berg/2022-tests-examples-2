package ru.yandex.metrika.schedulerd.cron.task;

import org.apache.commons.lang3.tuple.Pair;
import org.apache.logging.log4j.Level;
import org.joda.time.LocalDate;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.metrika.dbclients.mysql.IterableResultSet;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.segments.ApiUtilsTests;
import ru.yandex.metrika.segments.core.ApiUtils;
import ru.yandex.metrika.segments.core.parser.QueryParams;
import ru.yandex.metrika.segments.core.query.SampleAccuracy;
import ru.yandex.metrika.segments.core.secure.UserType;
import ru.yandex.metrika.tool.AllDatabases;
import ru.yandex.metrika.util.app.XmlPropertyConfigurer;
import ru.yandex.metrika.util.log.Log4jSetup;
import ru.yandex.metrika.util.time.DateTimeFormatters;

/**
 * Created by orantius on 21.11.16.
 */
@Ignore
public class SegmentUsersEstimationTaskTest {
    private static final Logger log = LoggerFactory.getLogger(SegmentUsersEstimationTaskTest.class);
    private MySqlJdbcTemplate template;
    private ApiUtils apiUtils;

    @Before
    public void setUp() throws Exception {
        template = AllDatabases.getTemplate("localhost", 3311, "metrika", XmlPropertyConfigurer.getTextFromFile("~/.mysql/pass_old"), "conv_main");
        ApiUtilsTests.setUp();
        apiUtils = ApiUtilsTests.apiUtils;
    }

    @Test
    public void execute() throws Exception {
        Log4jSetup.basicSetup(Level.INFO);

        SampleAccuracy accuracy = SampleAccuracy.low;
        LocalDate now = new LocalDate();
        LocalDate yesterday = now.minusDays(1);
        LocalDate weekAgo = now.minusDays(7);

        IterableResultSet<Pair<Integer, String>> query = template.queryStreaming("select counter_id, expression from segments where `status` = 'Active' " +
                        "order by segment_id limit 45000,1000000",
                (rs, i) -> {
                    return Pair.of(rs.getInt(1), rs.getString(2));
                });
        int i =0;
        for (Pair<Integer,String> filter : query) {
            i++;
            if(i%100==0) {
                System.out.println("i = " + i);
            }
            QueryParams queryParams = QueryParams.create()
                    //.counterId(21097177)
                    .counterId(filter.getLeft()) // 21097177
                    .startDate(weekAgo.toString(DateTimeFormatters.ISO_DTF))
                    .endDate(yesterday.toString(DateTimeFormatters.ISO_DTF))
                    .filtersBraces(filter.getRight())
                    /*.filtersBraces("((ym:s:regionCountry=='225')) and (ym:s:trafficSource=='organic') and (ym:s:advEngine!='ya_market') and " +
                            "(ym:s:searchPhrase=*'*тепловодох*' and ym:s:searchPhrase=*'*teplovodokhran*' and ym:s:searchPhrase=*'*тепловодоохран*' " +
                            "and ym:s:searchPhrase=*'*тепловохран*' and ym:s:searchPhrase=*'*пульсар*' and ym:s:searchPhrase=*'*пдтвх*' " +
                            "and ym:s:searchPhrase=*'*ктсптвх*' and ym:s:searchPhrase=*'*ntgkjdjl*' and ym:s:searchPhrase=*'*teplovodohran*' " +
                            "and ym:s:searchPhrase=*'*тепловодхран*' and ym:s:searchPhrase=*'*pulsarm*' and " +
                            "ym:s:searchPhrase=*'*тепловодокран*' and ym:s:searchPhrase=*'*тепло водохран*')")*/
                    .metrics("ym:s:users")
                    .sampleAccuracy(accuracy.name())
                    .ignoreLimits(true)
                    .limit(100)
                    .userType(UserType.MANAGER)
                    .priority("2")
                    .lang("ru")
                    .domain("");
            try {
                log.warn("filter = " + filter);
                String sql = apiUtils.toChQuery(apiUtils.parseQuery(queryParams));
                log.warn("sql = " + sql);
            } catch (Exception e) {
                log.error("counter_id = {}, filter = {}, date1 = {}, date2 = {}, sql = {}, error message = {}",
                        filter.getLeft(), filter, DateTimeFormatters.ISO_DTF.print(weekAgo), DateTimeFormatters.ISO_DTF.print(yesterday), filter, e.getMessage());
                //throw e;
            }

        }
    }

}
