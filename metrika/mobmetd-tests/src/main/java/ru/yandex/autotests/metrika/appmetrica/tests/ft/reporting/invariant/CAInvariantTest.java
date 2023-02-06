package ru.yandex.autotests.metrika.appmetrica.tests.ft.reporting.invariant;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Partner;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.*;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static java.util.Collections.singletonList;
import static org.hamcrest.CoreMatchers.*;
import static org.hamcrest.Matchers.closeTo;
import static org.hamcrest.number.OrderingComparison.greaterThan;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.YANDEX_METRO;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.data.Partner.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.Partners.ORGANIC;
import static ru.yandex.autotests.metrika.appmetrica.data.Partners.PORTAL;
import static ru.yandex.autotests.metrika.appmetrica.parameters.CAGroup.DAY;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;
import static ru.yandex.autotests.metrika.appmetrica.utils.Utils.listDifference;

/**
 * Created by graev on 25/03/2017.
 */
@Features(Requirements.Feature.DATA)
@Stories(Requirements.Story.COHORT_ANALYSIS)
@Title("Когортный анализ (инварианты)")
@RunWith(Parameterized.class)
public final class CAInvariantTest {
    private static final UserSteps user = UserSteps.onTesting(Users.SUPER_LIMITED);

    private static final Long APP_ID = YANDEX_METRO.get(Application.ID);

    private static final Double TOLERANCE_PERCENT = 3.0;

    @Parameterized.Parameter
    public Partner partner;

    @Parameterized.Parameter(1)
    public CAGroup group;

    @Parameterized.Parameter(2)
    public CARetention retention;

    public CohortAnalysisParameters parameters;

    @Parameterized.Parameters(name = "Partner: {0}; Group: {1}; Retention: {2}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .values(ORGANIC, PORTAL)
                .values(singletonList(DAY))
                .values(CARetention.CLASSIC, CARetention.ROLLING)
                .build();
    }

    @Before
    public void setup() {
        setCurrentLayerByApp(APP_ID);
        parameters = new CohortAnalysisParameters()
                .withId(APP_ID)
                .withAccuracy("0.1")
                .withConversion(CAConversion.sessionStart())
                .withDate1(apiProperties().getCaStartDate())
                .withDate2(apiProperties().getCaEndDate())
                .withMetric(CAMetric.DEVICES)
                .withGroup(group)
                .withRetention(retention);
    }

    @Test
    public void testPartnerPercents() {
        final List<Double> percentsFromGrouping = user.onCohortAnalysisSteps().partnerPercentsFromGrouping(partner.get(ID), parameters);
        final List<Double> percentsFromBucketTotals = user.onCohortAnalysisSteps().partnerPercentsFromBucketTotals(partner.get(ID), parameters);

        assumeThat("строки имеют одинаковую длину", percentsFromGrouping.size(), equalTo(percentsFromBucketTotals.size()));
        final List<Double> difference = listDifference(percentsFromGrouping, percentsFromBucketTotals);

        assertThat("проценты возвращаемости партнера похожи",
                difference, not(hasItem(greaterThan(TOLERANCE_PERCENT))));
    }

    @Test
    public void testPartnerTotals() {
        final Long totalsFromGrouping = user.onCohortAnalysisSteps().partnerTotalsFromGrouping(partner.get(ID), parameters);
        final Long totalsFromFilter = user.onCohortAnalysisSteps().partnerPercentsFromFilter(partner.get(ID), parameters);

        assertThat("число установок больше нуля", totalsFromGrouping, greaterThan(0L));

        assertThat("общее число установок по партнеру совпадает",
                (double) totalsFromFilter / totalsFromGrouping, closeTo(1.0, TOLERANCE_PERCENT / 100.0));
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }

}
