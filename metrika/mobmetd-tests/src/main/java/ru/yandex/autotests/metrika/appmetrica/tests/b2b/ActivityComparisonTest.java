package ru.yandex.autotests.metrika.appmetrica.tests.b2b;

import com.google.common.collect.ImmutableList;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.irt.testutils.beandiffer2.beanfield.BeanFieldPath;
import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.matchers.B2BMatchers;
import ru.yandex.autotests.metrika.appmetrica.parameters.ActivityParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.model.ApplicationActivity;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.*;
import static ru.yandex.autotests.metrika.appmetrica.matchers.B2BMatchers.similarTo;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;


@Features(Requirements.Feature.DATA)
@Stories(Requirements.Story.ACTIVITY)
@Title("Активность")
public class ActivityComparisonTest {

    /**
     * Активность считается за последние дни, за которые постоянно доходят данные
     */
    private static final double EPSILON = 0.05;

    private static final UserSteps testingSteps = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiTesting())
            .withUser(Users.SUPER_LIMITED)
            .build();

    private static final UserSteps referenceSteps = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiReference())
            .withUser(Users.SUPER_LIMITED)
            .build();

    private static final BeanFieldPath[] VOLATILE_FIELDS = Stream.of("activeUsers", "newUsers", "sessions")
            .map(name -> BeanFieldPath.newPath(".*", name))
            .toArray(BeanFieldPath[]::new);

    private ActivityParameters parameters;

    @Before
    public void setup() {
        parameters = new ActivityParameters()
                .withIds(ImmutableList.of(YANDEX_REALTY, YANDEX_DISK, YANDEX_METRO, PUSH_SAMPLE, ANDROID_APP).stream()
                        .map(a -> a.get(Application.ID))
                        .collect(Collectors.toList()));
    }

    @Test
    public void checkReportsMatch() {
        final List<ApplicationActivity> actual = testingSteps.onReportSteps().getActivities(parameters);
        final List<ApplicationActivity> expected = referenceSteps.onReportSteps().getActivities(parameters);
        assertThat("отчеты совпадают", actual,
                B2BMatchers.similarTo(expected, VOLATILE_FIELDS, new BeanFieldPath[0], EPSILON));
    }
}
