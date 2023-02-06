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
public class AllureStoryRule extends TestWatcher {
    private List<String> stories;

    public AllureStoryRule(List<String> stories) {
        this.stories = stories;
    }

    public AllureStoryRule(String... stories) {
        this(Arrays.asList(stories));
    }

    @Override
    protected void starting(Description description) {
        stories.forEach((story) -> Allure.LIFECYCLE.fire(
                (TestCaseResult testCaseResult) -> testCaseResult.getLabels()
                        .add(AllureModelUtils.createStoryLabel(story)))
        );
    }
}
