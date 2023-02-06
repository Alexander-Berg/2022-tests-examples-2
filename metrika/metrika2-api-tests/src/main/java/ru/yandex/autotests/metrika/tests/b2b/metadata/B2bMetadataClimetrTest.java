package ru.yandex.autotests.metrika.tests.b2b.metadata;

import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1MetadataClimetrGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1MetadataClimetrCounterIdGETSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanDiffer;
import static ru.yandex.autotests.irt.testutils.beandiffer.beanconstraint.BeanConstraints.ignore;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_METRIKA;

/**
 * Created by orantius on 14.12.16.
 */
@Features({Requirements.Feature.DATA, Requirements.Feature.CLIMETR})
@Stories(Requirements.Story.Report.METADATA)
@Title("B2B - Метаданные мобильного приложения")
public class B2bMetadataClimetrTest {

    protected static final UserSteps userOnTest = new UserSteps();
    protected static final UserSteps userOnRef = new UserSteps().useReference();
    protected static final Counter COUNTER = YANDEX_METRIKA;

    @Test
    public void check() {
        StatV1MetadataClimetrGETSchema referenceBean = userOnRef.onMetadataSteps().getClimetrConfig();
        StatV1MetadataClimetrGETSchema testingBean = userOnTest.onMetadataSteps().getClimetrConfig();
        assertThat("при несовпадении ответов проверять интеграцию с мобильным приложением",
                testingBean, beanDiffer(referenceBean).fields(ignore("profile")));
    }

    @Test
    public void checkForCounter() {
        StatV1MetadataClimetrCounterIdGETSchema referenceBean = userOnRef.onMetadataSteps().getClimetrConfig(COUNTER.getId());
        StatV1MetadataClimetrCounterIdGETSchema testingBean = userOnTest.onMetadataSteps().getClimetrConfig(COUNTER.getId());
        assertThat("при несовпадении ответов проверять интеграцию с мобильным приложением",
                testingBean, beanDiffer(referenceBean).fields(ignore("profile")));
    }

}
