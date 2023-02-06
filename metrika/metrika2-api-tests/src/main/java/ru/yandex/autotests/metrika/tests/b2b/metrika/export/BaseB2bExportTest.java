package ru.yandex.autotests.metrika.tests.b2b.metrika.export;

import java.util.List;

import org.junit.Rule;
import org.junit.Test;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.irt.testutils.beandiffer.matchvariation.DefaultMatchVariation;
import ru.yandex.autotests.irt.testutils.beandiffer.matchvariation.MatchVariation;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataCsvSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataXlsxSchema;
import ru.yandex.autotests.metrika.commons.rules.ParametersIgnoreRule;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.properties.MetrikaApiProperties;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.tests.utils.DoubleDiffer;

import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by sourx on 06.06.16.
 */
public class BaseB2bExportTest {

    @Rule
    public ParametersIgnoreRule parametersIgnoreRule = new ParametersIgnoreRule();

    protected static final UserSteps userOnTest = new UserSteps().withDefaultAccuracy();
    protected static final UserSteps userOnRef = new UserSteps().useReference().withDefaultAccuracy();

    private final MatchVariation doubleWithAccuracy = new DefaultMatchVariation()
            .forClasses(Double.class)
            .use(new DoubleDiffer(MetrikaApiProperties.getInstance().getDoubleDelta(), true));

    protected RequestType<?> requestType;
    protected IFormParameters reportParameters;

    @Test
    public void checkXlsx() {
        StatV1DataXlsxSchema referenceBean = userOnRef.onReportSteps()
                .getXlsxReport(requestType, reportParameters);
        StatV1DataXlsxSchema testingBean = userOnTest.onReportSteps()
                .getXlsxReport(requestType, reportParameters);

        List<List<Object>> referenceData = userOnRef.onResultSteps().getDataFromXlsx(referenceBean);

        List<List<Object>> testingData = userOnTest.onResultSteps().getDataFromXlsx(testingBean);

        assertThat("ответы совпадают", testingData, beanEquivalent(referenceData).withVariation(doubleWithAccuracy));
    }

    @Test
    public void checkCsv() {
        StatV1DataCsvSchema referenceBean = userOnRef.onReportSteps()
                .getCsvReport(requestType, reportParameters);
        StatV1DataCsvSchema testingBean = userOnTest.onReportSteps()
                .getCsvReport(requestType, reportParameters);

        List<List<Object>> referenceData = userOnRef.onResultSteps().getDataFromCsv(referenceBean);

        List<List<Object>> testingData = userOnTest.onResultSteps().getDataFromCsv(testingBean);

        assertThat("ответы совпадают", testingData, beanEquivalent(referenceData).withVariation(doubleWithAccuracy));
    }

}
