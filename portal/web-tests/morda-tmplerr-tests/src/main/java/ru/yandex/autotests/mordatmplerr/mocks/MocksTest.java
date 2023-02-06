package ru.yandex.autotests.mordatmplerr.mocks;

import org.apache.log4j.Logger;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordatmplerr.Properties;
import ru.yandex.autotests.mordatmplerr.data.DataProvider;
import ru.yandex.autotests.mordatmplerr.mordatypes.Morda;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.Collection;

import static ru.yandex.autotests.mordacommonsteps.matchers.DocumentLoadedMatcher.contentLoaded;
import static ru.yandex.qatools.htmlelements.matchers.MatcherDecorators.should;
import static ru.yandex.qatools.htmlelements.matchers.MatcherDecorators.timeoutHasExpired;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 20.03.14
 */
@Aqua.Test(title = "Mocks")
@Features("Mocks")
@RunWith(Parameterized.class)
public class MocksTest {
    private static final Properties CONFIG = new Properties();
    private static final Logger LOG = Logger.getLogger(MocksTest.class);
    public static final String MOCK = "mock";

    @Rule
    public MordaAllureBaseRule rule;
    private Morda morda;
    private CommonMordaSteps user;
    private WebDriver driver;

    @Parameterized.Parameters(name = "{0}, {1}")
    public static Collection<Object[]> data() {
        return DataProvider.getTestData();
    }

    public MocksTest(String mock, Morda morda) {
        this.rule = morda.getRule();
        this.driver = rule.getDriver();
        this.morda = morda.withParameter(MOCK, mock);
        this.user = new CommonMordaSteps(driver);
    }

    @Test
    public void mock() {
        String url = morda.getUrl(CONFIG.getMordaEnv().getEnv());
        LOG.info(url);
        user.opensPage(url);
        user.opensPage(url);
        should(contentLoaded()).whileWaitingUntil(timeoutHasExpired()).matches(driver);
        user.screenshot();
    }
}
