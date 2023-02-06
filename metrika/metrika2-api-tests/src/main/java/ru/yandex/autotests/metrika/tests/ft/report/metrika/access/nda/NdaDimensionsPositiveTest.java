package ru.yandex.autotests.metrika.tests.ft.report.metrika.access.nda;

import org.apache.commons.lang3.tuple.Pair;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.stream.Stream;

import static com.google.common.collect.ImmutableList.of;
import static java.util.function.Function.identity;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_METRIKA_2_0;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.nda;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.table;

@Features(Requirements.Feature.NDA)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.METADATA})
@Title("Доступ к измерениям NDA в отчетах")
@RunWith(Parameterized.class)
public class NdaDimensionsPositiveTest {

    private static final Counter COUNTER = YANDEX_METRIKA_2_0;

    public static final String METRIC_VISITS = "ym:s:visits";
    public static final String METRIC_HITS = "ym:pv:pageviews";
    public static final String METRIC_EXTERNAL_LINK = "ym:el:links";
    public static final String METRIC_DOWNLOAD = "ym:dl:blockedPercentage";
    public static final String METRIC_SHARE_SERVICES = "ym:sh:users";

    protected static final UserSteps userTest = new UserSteps().withDefaultAccuracy();

    private static UserSteps user;

    @Parameterized.Parameter(0)
    public String title;

    @Parameterized.Parameter(1)
    public User currentUser;

    @Parameterized.Parameter(2)
    public String dimensionName;

    @Parameterized.Parameter(3)
    public Holder holder;

    private static final class Holder {
        private FreeFormParameters tail = makeParameters();

        public FreeFormParameters getTail() {
            return tail;
        }
    }

    @Parameterized.Parameters(name = "Доступ: {0}, пользователь: {1}, измерение {2}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .vectorValues(
                        of("суперпользователь", SUPER_USER),
                        of("менеджер", MANAGER),
                        of("менеджер-директ", MANAGER_DIRECT),
                        of("пользователь с правом чтения счетчика idm", USER_WITH_IDM_VIEW_PERMISSION),
                        of("пользователь с правом редактирования счетчика idm", USER_WITH_IDM_EDIT_PERMISSION),
                        of("саппорт", SUPPORT))
                .vectorValues(MultiplicationBuilder.<String, String, Holder>builder(
                        userTest.onMetadataSteps().getDimensions(nda()), Holder::new)
                        .apply(table(TableEnum.VISITS),
                                (m, h) -> {
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withMetric(METRIC_VISITS));
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(table(TableEnum.HITS),
                                (m, h) -> {
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withMetric(METRIC_HITS));
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(table(TableEnum.DOWNLOADS),
                                (m, h) -> {
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withMetric(METRIC_DOWNLOAD));
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(table(TableEnum.EXTERNAL_LINKS),
                                (m, h) -> {
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withMetric(METRIC_EXTERNAL_LINK));
                                    return Stream.of(Pair.of(m, h));
                                })
                        .apply(table(TableEnum.SHARE_SERVICES),
                                (m, h) -> {
                                    h.getTail().append(
                                            new CommonReportParameters()
                                                    .withMetric(METRIC_SHARE_SERVICES));
                                    return Stream.of(Pair.of(m, h));
                                })
                        .buildVectorValues(identity()))
                .build();
    }

    @Before
    public void setup() {
        user = new UserSteps().withDefaultAccuracy().withUser(currentUser);
    }

    @Test
    public void accessUserSuccess() {
        user.onReportSteps().getTableReportAndExpectSuccess(
                new CommonReportParameters()
                        .withDimension(dimensionName)
                        .withId(COUNTER.get(ID)),
                holder.getTail());
    }
}
