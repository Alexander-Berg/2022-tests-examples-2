package ru.yandex.autotests.mordamobile.afisha;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.autotests.mordamobile.steps.AfishaSteps;
import ru.yandex.qatools.allure.annotations.Features;

import static ru.yandex.autotests.mordamobile.data.AfishaData.TITLE_LINK;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
@Aqua.Test(title = "Блок афиши")
@Features("Afisha")
public class AfishaTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private AfishaSteps userAfisha = new AfishaSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Before
    public void setUp() throws Exception {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        user.shouldSeeElement(homePage.afishaBlock);
    }

    @Test
    public void afishaTitle() {
        user.shouldSeeLink(homePage.afishaBlock.title, TITLE_LINK);
    }

    @Test
    public void afishaLinks() {
        userAfisha.shouldSeeAfishaLinks();
    }

    @Test
    public void afishaGenres() {
        userAfisha.shouldSeeAfishaGenres();
    }

    @Test
    public void afishaIcon() {
        user.shouldSeeElement(homePage.afishaBlock.icon);
    }
}
