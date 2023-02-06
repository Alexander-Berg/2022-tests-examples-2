package ru.yandex.autotests.mordatmplerr.xss;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.Keys;
import org.openqa.selenium.UnhandledAlertException;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordatmplerr.Properties;
import ru.yandex.autotests.mordatmplerr.mordatypes.HwBmwMorda;
import ru.yandex.autotests.mordatmplerr.mordatypes.HwLgMorda;
import ru.yandex.autotests.mordatmplerr.mordatypes.Morda;
import ru.yandex.autotests.mordatmplerr.pages.HomePage;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.instanceOf;
import static org.hamcrest.Matchers.not;
import static org.junit.Assert.fail;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.mordatmplerr.mordatypes.BetaMorda.betaMorda;
import static ru.yandex.autotests.mordatmplerr.mordatypes.ComTrMorda.comTrMorda;
import static ru.yandex.autotests.mordatmplerr.mordatypes.HwBmwMorda.hwBmwMorda;
import static ru.yandex.autotests.mordatmplerr.mordatypes.HwLgMorda.hwLgMorda;
import static ru.yandex.autotests.mordatmplerr.mordatypes.MainMorda.mainMorda;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 23.04.14
 */
@Aqua.Test(title = "DOM XSS")
@Features("DOM XSS")
@RunWith(Parameterized.class)
public class DomXssTest {
    private static final Properties CONFIG = new Properties();
    private static final String ALLERT_SCRIPT =
            "#%27%3E%27%3E%22%3E%3Cimg/src=%27x%27onerror=alert%28document.domain%29%3E";

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();
    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Morda> data = new ArrayList<>();
        data.add(mainMorda(RU));
        data.add(comTrMorda());
        data.add(hwBmwMorda());
        data.add(hwLgMorda());
        return ParametrizationConverter.convert(data);
    }

    private Morda morda;

    public DomXssTest(Morda morda) {
        this.morda = morda;
    }

    @Test
    public void xssUrl() {
        try {
            user.opensPage(morda.getUrl(CONFIG.getMordaEnv().getEnv()) + ALLERT_SCRIPT);
        } catch (UnhandledAlertException e) {
            fail("Should not see alert");
        }
    }

    @Test
    public void xssInput() {
        assumeThat(morda, not(anyOf(instanceOf(HwBmwMorda.class), instanceOf(HwLgMorda.class))));
        user.opensPage(morda.getUrl(CONFIG.getMordaEnv().getEnv()));
        user.shouldSeeElement(homePage.input);
        try {
            user.entersTextInInput(homePage.input, ALLERT_SCRIPT);
            homePage.input.sendKeys(Keys.ENTER);
        } catch (UnhandledAlertException e) {
            fail("Should not see alert");
        }
    }
}
