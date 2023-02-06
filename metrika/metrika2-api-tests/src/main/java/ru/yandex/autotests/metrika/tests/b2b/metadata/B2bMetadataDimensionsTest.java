package ru.yandex.autotests.metrika.tests.b2b.metadata;

import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.constructor.response.DimensionMetaExternal;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanDiffer;
import static ru.yandex.autotests.irt.testutils.beandiffer.beanconstraint.BeanConstraints.ignore;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.any;

/**
 * Created by orantius on 14.12.16.
 */
@Features({Requirements.Feature.DATA, Requirements.Feature.JSON_SCHEMAS})
@Stories(Requirements.Story.Report.METADATA)
@Title("B2B - Метаданные атрибутов")
public class B2bMetadataDimensionsTest  {

    protected static final UserSteps userOnTest = new UserSteps();
    protected static final UserSteps userOnRef = new UserSteps().useReference();

    @Test
    public void check() {
        Collection<DimensionMetaExternal> referenceBean = userOnRef.onMetadataSteps().getDimensionsMeta(any());
        Collection<DimensionMetaExternal> testingBean = userOnTest.onMetadataSteps().getDimensionsMeta(any());
        assertThat("internal_type атрибутов должен совпадать, " +
                        "при несовпадении проверяем интеграцию с интерфейсом сохраненных фильтров с этим атрибутом!",
                testingBean, beanDiffer(referenceBean).fields(ignore("profile")));
    }

}
