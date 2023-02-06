package ru.yandex.autotests.advapi.api.tests.b2b.reports;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.advapi.api.tests.utils.DoubleDiffer;
import ru.yandex.autotests.advapi.data.common.RequestType;
import ru.yandex.autotests.advapi.properties.AdvApiProperties;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.irt.testutils.beandiffer.beanconstraint.BeanConstraint;
import ru.yandex.autotests.irt.testutils.beandiffer.matchvariation.DefaultMatchVariation;
import ru.yandex.autotests.irt.testutils.beandiffer.matchvariation.MatchVariation;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParametersList;
import ru.yandex.autotests.metrika.commons.rules.ParametersIgnoreRule;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static java.util.Collections.addAll;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.advapi.data.users.Users.SUPER_USER;
import static ru.yandex.autotests.advapi.steps.report.MetadataSteps.Predicates.*;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.irt.testutils.beandiffer.beanconstraint.BeanConstraints.ignore;

/**
 * Created by omaz on 12.12.14.
 */
@RunWith(Parameterized.class)
public abstract class BaseB2bTest {

    @Rule
    public ParametersIgnoreRule parametersIgnoreRule = new ParametersIgnoreRule();

    private static final String[] ignoredFields = getIgnoredFields();
    protected MatchVariation doubleWithAccuracy = new DefaultMatchVariation()
            .forClasses(Double.class).use(new DoubleDiffer(AdvApiProperties.getInstance().getDoubleDelta()));

    protected static final UserSteps userOnTest = UserSteps.withUser(SUPER_USER).useTesting().withDefaultAccuracy();
    protected static final UserSteps userOnRef = UserSteps.withUser(SUPER_USER).useReference().withDefaultAccuracy();
    protected RequestType<?> requestType;
    protected IFormParameters reportParameters;

    @Test
    @IgnoreParametersList({
            @IgnoreParameters(reason = "no_data", tag = "no_data")
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
        userOnTest.onResultSteps().assumeNotEmptyBoth(testingBean, referenceBean);
    }

    private static String[] getIgnoredFields() {
        List<String> ignoredFields = new ArrayList<>();

        if (AdvApiProperties.getInstance().getIgnoredFields() != null) {
            addAll(ignoredFields, AdvApiProperties.getInstance().getIgnoredFields());
        }

        if (AdvApiProperties.getInstance().getDefaultIgnoredFields() != null) {
            for (String ignoredField : AdvApiProperties.getInstance().getDefaultIgnoredFields()) {
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

    // пока для этого нет данных
    // как появяться, нужно поменять кампанию и/или даты
    @IgnoreParameters.Tag(name = "no_data")
    public static Collection<Object[]> ignoreParameters() {
        return asList(new Object[][]{
                {matches(anyOf(
                        containsString("Visible"),
                        containsString("Sound"),
                        containsString("fullscreen"),
                        containsString("impressions")
                )), anything()}
        });
    }
}
