package ru.yandex.autotests.metrika.tests.b2b;

import java.util.ArrayList;
import java.util.List;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.irt.testutils.beandiffer.beanconstraint.BeanConstraint;
import ru.yandex.autotests.irt.testutils.beandiffer.matchvariation.DefaultMatchVariation;
import ru.yandex.autotests.irt.testutils.beandiffer.matchvariation.MatchVariation;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParametersList;
import ru.yandex.autotests.metrika.commons.rules.ParametersIgnoreRule;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.properties.MetrikaApiProperties;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.tests.utils.DoubleDiffer;

import static java.util.Collections.addAll;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.irt.testutils.beandiffer.beanconstraint.BeanConstraints.ignore;
import static ru.yandex.autotests.metrika.properties.MetrikaApiProperties.getInstance;

/**
 * Created by omaz on 12.12.14.
 */
@RunWith(Parameterized.class)
public abstract class BaseB2bTest {

    @Rule
    public ParametersIgnoreRule parametersIgnoreRule = new ParametersIgnoreRule();

    protected static final UserSteps userOnTest = new UserSteps().withDefaultAccuracy();
    protected static final UserSteps userOnRef = new UserSteps().useReference().withDefaultAccuracy();

    private static final String[] ignoredFields = getIgnoredFields();

    protected final MatchVariation doubleWithAccuracy = new DefaultMatchVariation()
            .forClasses(Double.class)
            .use(new DoubleDiffer(MetrikaApiProperties.getInstance().getDoubleDelta(), true));

    protected RequestType<?> requestType;
    protected IFormParameters reportParameters;

    @Test
    @IgnoreParametersList({
            @IgnoreParameters(reason = "no data", tag = "no data"),
            @IgnoreParameters(reason = "METR-26049", tag = "METR-26049"),
            @IgnoreParameters(reason = "METR-23460", tag = "pvl"),
            @IgnoreParameters(reason = "METRIQA-3319", tag = "METRIQA-3319"),
            @IgnoreParameters(reason = "METR-39392", tag = "METR-39392")
    })
    public void check() {
        Object referenceBean = userOnRef.onReportSteps().getRawReport(requestType, reportParameters);
        Object testingBean = userOnTest.onReportSteps().getRawReport(requestType, reportParameters);

        assumeOnResponses(testingBean, referenceBean);

        assertThat("ответы совпадают", testingBean, beanEquivalent(referenceBean).fields(getIgnore()).withVariation(doubleWithAccuracy));
    }

    /**
     * дополнительная проверка ожиданий относительно ответов тестируемой и образцовой систем
     *
     * @param testingBean   - ответ от тестируемой среды
     * @param referenceBean - ответ от образцовой среды
     */
    protected void assumeOnResponses(Object testingBean, Object referenceBean) {
        userOnTest.onResultSteps().assumeSimilarErrorCode(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeSuccessBoth(testingBean, referenceBean);
    }

    private static String[] getIgnoredFields() {
        List<String> ignoredFields = new ArrayList<>();

        if (getInstance().getIgnoredFields() != null) {
            addAll(ignoredFields, getInstance().getIgnoredFields());
        }

        if (getInstance().getDefaultIgnoredFields() != null) {
            for (String ignoredField : getInstance().getDefaultIgnoredFields()) {
                if (!ignoredFields.contains(ignoredField)) {
                    ignoredFields.add(ignoredField);
                }
            }
        }

        return ignoredFields.toArray(new String[ignoredFields.size()]);
    }

    public static BeanConstraint getIgnore() {
        return ignore(ignoredFields);
    }

}
