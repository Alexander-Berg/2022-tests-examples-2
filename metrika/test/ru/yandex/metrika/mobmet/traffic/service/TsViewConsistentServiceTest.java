package ru.yandex.metrika.mobmet.traffic.service;

import java.util.Collection;
import java.util.List;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableList;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.mobmet.model.UserContext;
import ru.yandex.metrika.mobmet.traffic.model.TsDimensionValue;
import ru.yandex.metrika.mobmet.traffic.model.TsMeta;
import ru.yandex.metrika.mobmet.traffic.model.TsMetricValue;
import ru.yandex.metrika.mobmet.traffic.model.TsRequest;
import ru.yandex.metrika.mobmet.traffic.model.TsResponse;
import ru.yandex.metrika.mobmet.traffic.model.TsResponseImpl;
import ru.yandex.metrika.mobmet.traffic.model.TsRow;
import ru.yandex.metrika.mobmet.traffic.model.TsRows;
import ru.yandex.metrika.mobmet.traffic.model.TsSegment;
import ru.yandex.metrika.mobmet.traffic.model.TsTotals;
import ru.yandex.metrika.mobmet.traffic.model.entity.metrics.TsClicksMetric;
import ru.yandex.metrika.mobmet.traffic.model.entity.metrics.TsSessionsMetric;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.containsString;
import static ru.yandex.metrika.mobmet.model.UserContext.unrestricted;


@RunWith(Parameterized.class)
public class TsViewConsistentServiceTest {

    public static final List<List<String>> events = List.of(List.of("foo"));

    private static final TsRequest request = TsRequest.builder()
            .withSegment(new TsSegment(42, "2017-04-01",
                    "2017-04-07", null, null, null, false, null))
            .withEvents(events)
            .build();

    private static final TsResponse nonZeroed = new TsResponseImpl(
            new TsRows(List.of(
                    new TsRow(List.of(TsDimensionValue.idName("id", "name")),
                            List.of(new TsMetricValue(new TsClicksMetric(), 10.0), new TsMetricValue(new TsSessionsMetric(), 8.0))),
                    new TsRow(List.of(TsDimensionValue.idName("id", "name")),
                            List.of(new TsMetricValue(new TsClicksMetric(), 4.0), new TsMetricValue(new TsSessionsMetric(), 1.0)))
            )),
            10,
            new TsTotals(List.of(new TsMetricValue(new TsClicksMetric(), 14.0), new TsMetricValue(new TsSessionsMetric(), 9.0))),
            new TsMeta(TsMeta.UserStat.ALL));

    private static final TsResponse zeroed = new TsResponseImpl(
            new TsRows(List.of(
                    new TsRow(List.of(TsDimensionValue.idName("id", "name")),
                            List.of(new TsMetricValue(new TsClicksMetric(), 10.0), new TsMetricValue(new TsSessionsMetric(), null))),
                    new TsRow(List.of(TsDimensionValue.idName("id", "name")),
                            List.of(new TsMetricValue(new TsClicksMetric(), 4.0), new TsMetricValue(new TsSessionsMetric(), null)))
            )),
            10,
            new TsTotals(List.of(new TsMetricValue(new TsClicksMetric(), 14.0), new TsMetricValue(new TsSessionsMetric(), null))),
            new TsMeta(TsMeta.UserStat.NONE));

    private static final TsReportService origin = (request, context) -> nonZeroed;

    // I am sorry for nulls, but there is no other way to create fake entity
    private static final UserContext context = unrestricted(null, null);

    @Parameterized.Parameter
    public String viewCreationDate;

    @Parameterized.Parameter(1)
    public TsResponse expectedResponse;

    @Parameterized.Parameters(name = "CreationDate: {0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                param("2017-05-01", zeroed), // Completely past request
                param("2017-04-03", zeroed), // Middle request
                param("2017-03-01", nonZeroed) // Future request
        );
    }

    @Test
    public void testZeroing() throws JsonProcessingException {
        final TsReportService consistent = new TsViewConsistentService(viewCreationDate, origin);

        final TsResponse actual = consistent.report(request, context);

        final String actualJson = new ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(actual);
        final String expectedJson = new ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(expectedResponse);

        assertThat(actualJson, containsString(expectedJson));
    }

    private static Object[] param(String creationDate, TsResponse expectedResponse) {
        return new Object[]{creationDate, expectedResponse};
    }

}
