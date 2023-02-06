package ru.yandex.autotests.metrika.tests.b2b.metrika.particulars;

import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.VisitorInfoReportParameters;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bParticularTest;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;

@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Report.MANUAL_SAMPLES, Requirements.Story.Report.Type.VISITORS_GRID})
@Title("B2B на отобранных вручную параметрах запросов VisitorsGrid")
public class ParticularsB2bVisitorsGridTest extends BaseB2bParticularTest {

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return of(
                createParams("METR-31319 503 IndexOutOfBoundsException в /stat/v1/user/info",
                        RequestTypes.VISITOR_INFO,
                        new VisitorInfoReportParameters()
                                .withFirstVisitDate("2022-04-08")
                                .withUserIDHash("2210675941")
                                .withUserIDHash64("13989665610822983512")
                                .withId(24226447L)),
                createParams("METR-30147 duplicate key",
                        RequestTypes.VISITOR_INFO,
                        new VisitorInfoReportParameters()
                                .withUserIDHash("2103230872")
                                .withUserIDHash64("9308889301051382922")
                                .withFirstVisitDate("2017-10-03")
                                .withId(44678152L))
        );
    }
}
