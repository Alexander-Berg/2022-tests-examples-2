package ru.yandex.autotests.metrika.tests.ft.report.metrika.access.nda;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.filters.Expression;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.MELDA_RU;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.errors.ReportError.WRONG_ATTRIBUTE_REAL;
import static ru.yandex.autotests.metrika.filters.Relation.exists;
import static ru.yandex.autotests.metrika.filters.Term.dimension;

@Features(Requirements.Feature.NDA)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.METADATA})
@Title("Доступ к атрибутам NDA в сегментации, негативные тесты")
@RunWith(Parameterized.class)
public class NdaAttributesFiltersNegativeTest {

    private static final User OWNER = METRIKA_TEST_COUNTERS;
    private static final User GUEST_VIEW = SIMPLE_USER6;
    private static final User GUEST_EDIT = SIMPLE_USER5;

    private static final Long COUNTER_ID = MELDA_RU.getId();

    public static final String METRIC = "ym:s:visits";
    public static final String DIMENSION = "ym:s:gender";

    private static final String USER_ID_VISITS = "ym:s:userID";
    private static final String USER_ID_HITS = "ym:pv:userID";

    private static UserSteps user;
    private static UserSteps userOwner;

    @Parameterized.Parameter(0)
    public String title;

    @Parameterized.Parameter(1)
    public User currentUser;

    @Parameterized.Parameter(2)
    public Expression filter;

    @Parameterized.Parameters(name = "Доступ: {0}, пользователь: {1}, измерение {2}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .vectorValues(
                        of("владелец обычный пользователь", OWNER),
                        of("гостевой доступ на чтение", GUEST_VIEW),
                        of("гостевой доступ на редактирование", GUEST_EDIT))
                .values(
                        exists(USER_ID_VISITS, dimension("ym:s:counterIDSerial").equalTo("1")),
                        exists(USER_ID_VISITS, dimension("ym:s:counterClass").defined()),
                        exists(USER_ID_VISITS, dimension("ym:s:userIDString").defined()),
                        exists(USER_ID_VISITS, dimension("ym:s:hasYACLID").equalTo("no")),
                        exists(USER_ID_VISITS, dimension("ym:s:hasYDCLID").equalTo("no")),
                        exists(USER_ID_VISITS, dimension("ym:s:hasYMCLID").equalTo("no")),
                        exists(USER_ID_VISITS, dimension("ym:s:isYandex").equalTo("yes")),
                        exists(USER_ID_VISITS, dimension("ym:s:ip").defined()),
                        exists(USER_ID_VISITS, dimension("ym:s:isRobotInternal").equalTo("no")),
                        exists(USER_ID_VISITS, dimension("ym:s:isRobotInternalAntiFraud").equalTo("no")),
                        exists(USER_ID_VISITS, dimension("ym:s:CLID").defined()),
                        exists(USER_ID_VISITS, dimension("ym:s:networkType").equalTo("wifi")),
                        exists(USER_ID_VISITS, dimension("ym:s:yanIsAdBlock").equalTo("no")),
                        exists(USER_ID_VISITS, dimension("ym:s:turboPageID").defined()),
                        exists(USER_ID_VISITS, dimension("ym:s:experimentSystemID").defined()),
                        exists(USER_ID_VISITS, dimension("ym:s:experimentGroupID").defined()),
                        exists(USER_ID_VISITS, dimension("ym:s:experimentExpID").defined()),
                        exists(USER_ID_VISITS, dimension("ym:s:ip4").defined()),
                        exists(USER_ID_VISITS, dimension("ym:s:ip6").defined()),
                        exists(USER_ID_VISITS, dimension("ym:s:ASN").defined()),
                        exists(USER_ID_VISITS, dimension("ym:s:inYandexRegion").defined()),

                        exists(USER_ID_HITS, dimension("ym:pv:turboPageID").defined()),
                        exists(USER_ID_HITS, dimension("ym:sp:turboPageID").defined())
                )
                .build();
    }
    @BeforeClass
    public static void init() {
        userOwner = new UserSteps().withDefaultAccuracy().withUser(OWNER);
    }

    @Before
    public void setup() {
        user = new UserSteps().withDefaultAccuracy().withUser(currentUser);
    }

    @Test
    public void accessUserSuccess() {
        user.onReportSteps().getTableReportAndExpectError(
                WRONG_ATTRIBUTE_REAL,
                new CommonReportParameters()
                        .withMetric(METRIC)
                        .withDimension(DIMENSION)
                        .withFilters(filter == null ? null : filter.build())
                        .withId(COUNTER_ID));
    }
}
