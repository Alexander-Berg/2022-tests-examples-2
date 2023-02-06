package ru.yandex.autotests.morda.rules.allure;

import org.junit.rules.TestWatcher;
import org.junit.runner.Description;
import ru.yandex.qatools.allure.Allure;
import ru.yandex.qatools.allure.config.AllureModelUtils;
import ru.yandex.qatools.allure.model.TestCaseResult;

import java.util.Arrays;
import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/04/15
 */
public class AllureFeatureRule extends TestWatcher {
    private List<String> features;

    public AllureFeatureRule(List<String> features) {
        this.features = features;
    }

    public AllureFeatureRule(String... features) {
        this(Arrays.asList(features));
    }

    @Override
    protected void starting(Description description) {
        features.forEach((feature) -> Allure.LIFECYCLE.fire(
                        (TestCaseResult testCaseResult) -> testCaseResult.getLabels()
                                .add(AllureModelUtils.createFeatureLabel(feature)))
        );
    }
}
