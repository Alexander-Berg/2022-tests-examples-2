package ru.yandex.autotests.mordamobile.tv;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.autotests.mordamobile.steps.TvSteps;
import ru.yandex.qatools.allure.annotations.Features;

import static ru.yandex.autotests.mordamobile.data.TvData.getTitleLink;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
@Aqua.Test(title = "Блок ТВ")
@Features("Tv")
public class TvTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private TvSteps userTv = new TvSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Before
    public void setUp() throws Exception {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        user.shouldSeeElement(homePage.tvBlock);
    }

    @Test
    public void tvTitle() {
        user.shouldSeeLink(homePage.tvBlock.title, getTitleLink(CONFIG.getBaseDomain().getCapital()));
    }

    @Test
    public void tvLinks() {
        userTv.shouldSeeTvLinks(CONFIG.getBaseDomain().getCapital());
    }

    @Test
    public void tvEvents() {
        userTv.shouldSeeTvEvents();
    }

    @Test
    public void tvIcon() {
        user.shouldSeeElement(homePage.tvBlock.icon);
    }
}
