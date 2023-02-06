package ru.yandex.autotests.metrika.tests.b2b.partnersgoals;

import java.util.Collection;

import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.irt.testutils.beandiffer.beanconstraint.BeanConstraints.only;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Title("B2B - партнерские цели")
@Stories(Requirements.Story.Management.PARTNERS_GOALS)
public class B2BPartnersGoalsTest {

    private static final UserSteps userOnTest = new UserSteps();
    private static final UserSteps userOnRef = new UserSteps().useReference();

    @Test
    public void test() {
        Collection<String> testingAnswer = userOnTest.onMetadataSteps().getAllPartnersGoalsTypes();
        Collection<String> referenceAnswer = userOnRef.onMetadataSteps().getAllPartnersGoalsTypes();

        assertThat("ответы совпадают", testingAnswer,
                beanEquivalent(referenceAnswer).fields(only("action", "description", "name", "partner")));
    }
}
