package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.table;

import org.junit.Test;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.filters.Relation.exists;
import static ru.yandex.autotests.metrika.filters.Term.dimension;

/**
 * Created by sourx on 20.03.17.
 */
@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Report.MANUAL_SAMPLES, Requirements.Story.Report.Type.TABLE})
@Title("Фильтры: на отобранных вручную параметрах запросов Table")
public class ParticularsTableTest extends ParticularsBaseTableTest  {

    @Test
    public void check() {
        userOnTest.onReportSteps().getReportAndExpectSuccess(RequestTypes.TABLE, reportParameters);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return of(
                createParams("METR-25691 regex bug",
                        new TableReportParameters()
                                .withId(SENDFLOWERS_RU)
                                .withDate1("2016-08-16")
                                .withDate2("2016-08-22")
                                .withDimension("ym:s:age")
                                .withFilters(dimension("ym:s:searchPhrase").matchStar("*сон-мед*")
                                        .and(dimension("ym:s:searchPhrase").matchStar("*сон мед*"))
                                        .and(dimension("ym:s:searchPhrase").matchStar("*4957580000*"))
                                        .and(dimension("ym:s:searchPhrase").matchStar("*vtlkfqy*"))
                                        .and(dimension("ym:s:searchPhrase").matchStar("*млс*"))
                                        .and(dimension("ym:s:searchPhrase").matchStar("*мед*лай*"))
                                        .and(dimension("ym:s:searchPhrase").matchStar("*med*lin*")).build())
                                .withMetric("ym:s:visits")),
                createParams("METR-25690 regex bug",
                        new TableReportParameters()
                                .withId(SENDFLOWERS_RU)
                                .withDate1("2016-08-16")
                                .withDate2("2016-08-22")
                                .withDimension("ym:s:age")
                                .withFilters(dimension("ym:s:referalSource").matchRegEx("sa|ca|or|").build())
                                .withMetric("ym:s:visits")),
                createParams("METR-25692 regex bug",
                        new TableReportParameters()
                                .withId(SENDFLOWERS_RU)
                                .withDate1("2016-08-16")
                                .withDate2("2016-08-22")
                                .withDimension("ym:s:age")
                                .withFilters(dimension("ym:s:referalSource").matchStar("*sovet@*").build())
                                .withMetric("ym:s:visits")),
                createParams("METR-25693 ym:up:specialUser",
                        new TableReportParameters()
                                .withId(SENDFLOWERS_RU)
                                .withDate1("2016-08-16")
                                .withDate2("2016-08-22")
                                .withDimension("ym:up:paramsLevel1")
                                .withFilters(exists("ym:s:specialUser", dimension("ym:s:regionCity").in("2")).build())
                                .withMetric("ym:up:params"),
                        goalId(5133671L)),
                createParams("METR-44043 filter by counterIDName",
                        new TableReportParameters()
                                .withIds(46481424L,46167603L,46481436L,55496194L,47006268L,72998932L,54551818L,46481322L)
                                .withFilters(dimension("ym:s:counterIDName").in("demo.arctl.ru","uth.arctl.ru","etl.arctl.ru","kedr.arctl.ru","tetra.arctl.ru","quick.arctl.ru","tsg.arctl.ru").build())
                                .withMetric("ym:s:visits")
                                .withDimension("ym:s:deviceCategoryName")),
                createParams("METR-43773 check additional regexp validation",
                        new TableReportParameters()
                                .withId(SENDFLOWERS_RU)
                                .withDate1("2016-08-16")
                                .withDate2("2016-08-22")
                                .withDimension("ym:s:age")
                                .withFilters("ym:s:searchPhrase!~'дом\\\\sкофе|кофе\\\\\\\\дом|domcof|domkof|dom kof|coffeedom|cofedom|домкофе|кофедом|ljv rjat|\\\\.ru|\\\\.ру'")
                                .withMetric("ym:s:visits")
                ),
                createParams("METR-44830: added uniqUpTo10 for joins",
                        new TableReportParameters()
                                .withId(SENDFLOWERS_RU)
                                .withDate1("2021-06-28")
                                .withDate2("2021-06-30")
                                .withDimension("ym:ad:lastSignDirectOrder")
                                .withFilters("(EXISTS ym:pv:specialUser WITH (ym:pv:URLPathFull=*'*eventGA=reserve*')) and (EXISTS ym:s:specialUser WITH (ym:s:directClickOrder=='158767836')) and ym:ad:LastSignDirectOrder!n")
                                .withMetric("ym:ad:clicks")
                                .withDirectClientLogins("context-yndx-tv")
                )

        );
    }
}
