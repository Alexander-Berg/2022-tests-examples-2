package ru.yandex.autotests.audience.management.tests.experiments;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import ru.yandex.audience.pixel.Pixel;
import ru.yandex.audience.segmentab.ExperimentAB;
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
import static ru.yandex.autotests.audience.data.wrappers.WrapperBase.wrap;
import static ru.yandex.autotests.audience.management.tests.TestData.*;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.commons.beans.BeanDifferMatchers.hasBeanEquivalent;
import static ru.yandex.autotests.audience.parameters.ULoginParameters.ulogin;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

/**
 *
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.EXPERIMENTS})
@Title("Experiment: редактирование экспериментов")
@RunWith(Parameterized.class)
public class EditExperimentTest {
    private final User owner = USER_DELEGATOR;

    private ExperimentAB editedExperiment;
    private ExperimentAB expectedExperiment;
    private Long experimentId;
    private UserSteps userSteps;

    @Parameter
    public ExperimentAB newName;

    @Parameter(1)
    public User userParam;

    @Parameter(2)
    public String userDescription;

    @Parameterized.Parameters(name = "пользователь {2}, измененный эксперимент: {0}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .values(getSimpleExperiment(USER_DELEGATOR))
                .vectorValues(getSuperUser(), getUserWithPermEdit(), getOwner())
                .build();
    }

    @Before
    public void setup() {
        userSteps = UserSteps.withUser(userParam);
        ExperimentAB createdExperiment = userSteps.onExperimentSteps().createExperiment(getSimpleExperiment(owner), ulogin(owner));
        experimentId = createdExperiment.getExperimentId();

        expectedExperiment = wrap(createdExperiment).getClone();
        expectedExperiment.setName(newName.getName());
        expectedExperiment.setCounterIds(newName.getCounterIds());
        for (int i = 0; i < expectedExperiment.getSegments().size(); i++) {
            expectedExperiment.getSegments().get(i).setName(newName.getSegments().get(i).getName());
        }

        editedExperiment = userSteps.onExperimentSteps().editExperiment(experimentId, newName, ulogin(owner));
    }

    @Test
    public void checkEditExperiment() {
        assertThat("измененный эксперимент совпадает с ожидаемым", editedExperiment,
                equivalentTo(expectedExperiment));
    }

    @Test
    public void checkEditedExperimentInList() {
        List<ExperimentAB> experiments = userSteps.onExperimentSteps().getExperiments(ulogin(owner));

        assertThat("измененный эксперимент присутстует в списке", experiments,
                hasBeanEquivalent(ExperimentAB.class, expectedExperiment));
    }

    @After
    public void tearDown() {
        userSteps.onExperimentSteps().deleteExperimentAndIgnoreStatus(experimentId, ulogin(owner));
    }
}
