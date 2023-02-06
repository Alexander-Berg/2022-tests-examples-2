package ru.yandex.autotests.metrika.tests.b2b.metrika.particulars;

import java.util.Collection;

import com.google.common.collect.ImmutableList;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.filters.Term;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bParticularTest;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static com.google.common.collect.ImmutableList.of;
import static ru.yandex.autotests.metrika.filters.Term.dimension;

@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Report.MANUAL_SAMPLES, Requirements.Story.Report.Type.TABLE})
@Title("B2B на отобранных вручную параметрах запросов с многомерными массивами")
public class ParticularsB2bMultiDimensionalArrayTest extends BaseB2bParticularTest {

    private static final long COUNTER_DRIVE_2 = 33911514L;
    private static final String ACCURACY = "0.01";
    private static final String DATE_ADFOX = "2020-05-18";
    private static final String DATE_PUBLISHERS = "2021-11-18";

    private static final ImmutableList<String> METRICS_ADFOX = of("ym:s:visits", "ym:s:adfoxRequests");
    private static final ImmutableList<String> METRICS_PUBLISHERS = of("ym:s:visits", "ym:s:publisherviews");

    private static final Term FILTER_ADFOX_OWNER = dimension("ym:s:adfoxOwner").equalTo("59610");
    private static final Term FILTER_ADFOX_PUID_KEY = dimension("ym:s:adfoxPuidKey").equalTo("5");
    private static final Term FILTER_PUBLISHER_RUBRIC = dimension("ym:s:publisherArticleRubric").equalTo("DRIVE2");
    private static final Term FILTER_PUBLISHER_AUTHOR = dimension("ym:s:publisherArticleAuthor").equalTo("SergeyNicolaevic");
    private static final Term FILTER_PUBLISHER_TOPIC = dimension("ym:s:publisherArticleTopic").equalTo("аксессуары");

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                createParams("Adfox owners and puids without filter",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withId(COUNTER_DRIVE_2)
                                .withAccuracy(ACCURACY)
                                .withDimensions(of("ym:s:adfoxOwner", "ym:s:adfoxPuidKey", "ym:s:adfoxPuidValue"))
                                .withMetrics(METRICS_ADFOX)
                                .withDate1(DATE_ADFOX)
                                .withDate2(DATE_ADFOX)),
                createParams("Adfox owners and puids with filter by owner",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withId(COUNTER_DRIVE_2)
                                .withAccuracy(ACCURACY)
                                .withDimensions(of("ym:s:adfoxOwner", "ym:s:adfoxPuidKey", "ym:s:adfoxPuidValue"))
                                .withMetrics(METRICS_ADFOX)
                                .withFilters(FILTER_ADFOX_OWNER.build())
                                .withDate1(DATE_ADFOX)
                                .withDate2(DATE_ADFOX)),
                createParams("Adfox owners and puids with filter by puid key",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withId(COUNTER_DRIVE_2)
                                .withAccuracy(ACCURACY)
                                .withDimensions(of("ym:s:adfoxOwner", "ym:s:adfoxPuidKey", "ym:s:adfoxPuidValue"))
                                .withMetrics(METRICS_ADFOX)
                                .withFilters(FILTER_ADFOX_PUID_KEY.build())
                                .withDate1(DATE_ADFOX)
                                .withDate2(DATE_ADFOX)),
                createParams("Adfox owners and puids with filter by owner and puid key",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withId(COUNTER_DRIVE_2)
                                .withAccuracy(ACCURACY)
                                .withDimensions(of("ym:s:adfoxOwner", "ym:s:adfoxPuidKey", "ym:s:adfoxPuidValue"))
                                .withMetrics(METRICS_ADFOX)
                                .withFilters(FILTER_ADFOX_PUID_KEY.and(FILTER_ADFOX_OWNER).build())
                                .withDate1(DATE_ADFOX)
                                .withDate2(DATE_ADFOX)),
                createParams("Adfox owners with filter by puid key",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withId(COUNTER_DRIVE_2)
                                .withAccuracy(ACCURACY)
                                .withDimension("ym:s:adfoxOwner")
                                .withMetrics(METRICS_ADFOX)
                                .withFilters(FILTER_ADFOX_PUID_KEY.build())
                                .withDate1(DATE_ADFOX)
                                .withDate2(DATE_ADFOX)),
                createParams("Adfox owners with filter by owner and puid key",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withId(COUNTER_DRIVE_2)
                                .withAccuracy(ACCURACY)
                                .withDimension("ym:s:adfoxOwner")
                                .withMetrics(METRICS_ADFOX)
                                .withFilters(FILTER_ADFOX_PUID_KEY.and(FILTER_ADFOX_OWNER).build())
                                .withDate1(DATE_ADFOX)
                                .withDate2(DATE_ADFOX)),
                createParams("Publisher rubrics and authors without filter",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withId(COUNTER_DRIVE_2)
                                .withAccuracy(ACCURACY)
                                .withDimensions(of("ym:s:publisherArticleRubric", "ym:s:publisherArticleAuthor"))
                                .withMetrics(METRICS_PUBLISHERS)
                                .withDate1(DATE_PUBLISHERS)
                                .withDate2(DATE_PUBLISHERS)),
                createParams("Publisher rubrics and authors with filter by rubric",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withId(COUNTER_DRIVE_2)
                                .withAccuracy(ACCURACY)
                                .withDimensions(of("ym:s:publisherArticleRubric", "ym:s:publisherArticleAuthor"))
                                .withMetrics(METRICS_PUBLISHERS)
                                .withFilters(FILTER_PUBLISHER_RUBRIC.build())
                                .withDate1(DATE_PUBLISHERS)
                                .withDate2(DATE_PUBLISHERS)),
                createParams("Publisher rubrics and authors with filter by author",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withId(COUNTER_DRIVE_2)
                                .withAccuracy(ACCURACY)
                                .withDimensions(of("ym:s:publisherArticleRubric", "ym:s:publisherArticleAuthor"))
                                .withMetrics(METRICS_PUBLISHERS)
                                .withFilters(FILTER_PUBLISHER_AUTHOR.build())
                                .withDate1(DATE_PUBLISHERS)
                                .withDate2(DATE_PUBLISHERS)),
                createParams("Publisher rubrics and authors with filter by topic",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withId(COUNTER_DRIVE_2)
                                .withAccuracy(ACCURACY)
                                .withDimensions(of("ym:s:publisherArticleRubric", "ym:s:publisherArticleAuthor"))
                                .withMetrics(METRICS_PUBLISHERS)
                                .withFilters(FILTER_PUBLISHER_TOPIC.build())
                                .withDate1(DATE_PUBLISHERS)
                                .withDate2(DATE_PUBLISHERS)),
                createParams("Publisher rubrics and authors with filter by topic and author",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withId(COUNTER_DRIVE_2)
                                .withAccuracy(ACCURACY)
                                .withDimensions(of("ym:s:publisherArticleRubric", "ym:s:publisherArticleAuthor"))
                                .withMetrics(METRICS_PUBLISHERS)
                                .withFilters(FILTER_PUBLISHER_TOPIC.and(FILTER_PUBLISHER_AUTHOR).build())
                                .withDate1(DATE_PUBLISHERS)
                                .withDate2(DATE_PUBLISHERS)),
                createParams("Publisher rubrics and authors with filter by topic or author",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withId(COUNTER_DRIVE_2)
                                .withAccuracy(ACCURACY)
                                .withDimensions(of("ym:s:publisherArticleRubric", "ym:s:publisherArticleAuthor"))
                                .withMetrics(METRICS_PUBLISHERS)
                                .withFilters(FILTER_PUBLISHER_TOPIC.or(FILTER_PUBLISHER_AUTHOR).build())
                                .withDate1(DATE_PUBLISHERS)
                                .withDate2(DATE_PUBLISHERS)),
                createParams("Publisher rubrics, authors and topics without filter",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withId(COUNTER_DRIVE_2)
                                .withAccuracy(ACCURACY)
                                .withDimensions(of("ym:s:publisherArticleRubric", "ym:s:publisherArticleAuthor", "ym:s:publisherArticleTopic"))
                                .withMetrics(METRICS_PUBLISHERS)
                                .withDate1(DATE_PUBLISHERS)
                                .withDate2(DATE_PUBLISHERS)),
                createParams("Publisher rubrics, authors and topics with filter by rubric",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withId(COUNTER_DRIVE_2)
                                .withAccuracy(ACCURACY)
                                .withDimensions(of("ym:s:publisherArticleRubric", "ym:s:publisherArticleAuthor", "ym:s:publisherArticleTopic"))
                                .withMetrics(METRICS_PUBLISHERS)
                                .withFilters(FILTER_PUBLISHER_RUBRIC.build())
                                .withDate1(DATE_PUBLISHERS)
                                .withDate2(DATE_PUBLISHERS)),
                createParams("Publisher rubrics, authors and topics with filter by author",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withId(COUNTER_DRIVE_2)
                                .withAccuracy(ACCURACY)
                                .withDimensions(of("ym:s:publisherArticleRubric", "ym:s:publisherArticleAuthor", "ym:s:publisherArticleTopic"))
                                .withMetrics(METRICS_PUBLISHERS)
                                .withFilters(FILTER_PUBLISHER_AUTHOR.build())
                                .withDate1(DATE_PUBLISHERS)
                                .withDate2(DATE_PUBLISHERS)),
                createParams("Publisher rubrics, authors and topics with filter by topic",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withId(COUNTER_DRIVE_2)
                                .withAccuracy(ACCURACY)
                                .withDimensions(of("ym:s:publisherArticleRubric", "ym:s:publisherArticleAuthor", "ym:s:publisherArticleTopic"))
                                .withMetrics(METRICS_PUBLISHERS)
                                .withFilters(FILTER_PUBLISHER_TOPIC.build())
                                .withDate1(DATE_PUBLISHERS)
                                .withDate2(DATE_PUBLISHERS)),
                createParams("Publisher rubrics, authors and topics with filter by topic and author",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withId(COUNTER_DRIVE_2)
                                .withAccuracy(ACCURACY)
                                .withDimensions(of("ym:s:publisherArticleRubric", "ym:s:publisherArticleAuthor", "ym:s:publisherArticleTopic"))
                                .withMetrics(METRICS_PUBLISHERS)
                                .withFilters(FILTER_PUBLISHER_TOPIC.and(FILTER_PUBLISHER_AUTHOR).build())
                                .withDate1(DATE_PUBLISHERS)
                                .withDate2(DATE_PUBLISHERS)),
                createParams("Publisher rubrics, authors and topics with filter by topic or author",
                        RequestTypes.TABLE,
                        new TableReportParameters()
                                .withId(COUNTER_DRIVE_2)
                                .withAccuracy(ACCURACY)
                                .withDimensions(of("ym:s:publisherArticleRubric", "ym:s:publisherArticleAuthor", "ym:s:publisherArticleTopic"))
                                .withMetrics(METRICS_PUBLISHERS)
                                .withFilters(FILTER_PUBLISHER_TOPIC.or(FILTER_PUBLISHER_AUTHOR).build())
                                .withDate1(DATE_PUBLISHERS)
                                .withDate2(DATE_PUBLISHERS))
        );
    }
}
