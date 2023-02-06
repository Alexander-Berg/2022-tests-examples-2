package ru.yandex.autotests.audience.management.tests.experiments;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.audience.segmentab.ExperimentAB;
import ru.yandex.audience.segmentab.ExperimentSource;
import ru.yandex.autotests.audience.data.users.User;
import ru.yandex.autotests.audience.management.tests.Requirements;
import ru.yandex.autotests.audience.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.audience.data.users.Users.USER_DELEGATOR;
import static ru.yandex.autotests.audience.management.tests.TestData.getBkExperiment;
import static ru.yandex.autotests.audience.management.tests.TestData.getOwner;
import static ru.yandex.autotests.audience.management.tests.TestData.getSuperUser;
import static ru.yandex.autotests.audience.management.tests.TestData.getUserWithPermEdit;
import static ru.yandex.autotests.audience.parameters.ExperimentSourceParameters.source;
import static ru.yandex.autotests.audience.parameters.ULoginParameters.ulogin;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;

@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.EXPERIMENTS})
@Title("Experiments: создание эксперимента монетизации")
@RunWith(Parameterized.class)
public class CreateBkExperimentTest {

    private User owner = USER_DELEGATOR;
    private UserSteps userSteps;
    private ExperimentAB result;

    @Parameterized.Parameter
    public ExperimentAB request;

    @Parameterized.Parameter(1)
    public User user;

    @Parameterized.Parameter(2)
    public String userDescription;

    @Parameterized.Parameters(name = "пользователь: {2}, эксперимент: {0},")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .values(getBkExperiment(USER_DELEGATOR))
                .vectorValues(getSuperUser(), getUserWithPermEdit(), getOwner())
                .build();
    }

    @Before
    public void setup() {
        userSteps = UserSteps.withUser(user);

        result = userSteps.onExperimentSteps().createBkExperiment(request, ulogin(owner));
    }

    @Test
    public void checkCreatedExperiment() {
        assertThat("созданный эксперимент эквивалентен создаваемому", result,
                equivalentTo(request));
    }

    @Test
    public void checkExperimentInList() {
        List<ExperimentAB> experiments = userSteps.onExperimentSteps().getExperiments(ulogin(owner), source(ExperimentSource.BK));

        assertThat("созданный эксперимент присутствует в списке", experiments,
                hasBeanEquivalent(ExperimentAB.class, result));
    }


    @After
    public void tearDown() {
        userSteps.onExperimentSteps().deleteExperimentAndIgnoreStatus(result.getExperimentId(), ulogin(owner));
    }

}
