package ru.yandex.autotests.mainmorda.commontests.promo;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.PromoSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;

import static ru.yandex.autotests.mainmorda.data.PromoData.AWAPS_HREF_PATTERN;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.VALUE;

/**
 * User: alex89
 * Date: 09.04.12
 */
@Aqua.Test(title = "Появление баннера и параметры")
@Features({"Main", "Common", "Banner"})
public class BannerTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private PromoSteps userPromo = new PromoSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void initLanguage() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        user.opensPage("http://awaps.yandex.ru/?adt_id=82599");
        userPromo.shouldSeeAdtIdOnAwapsPage("82599");
        user.opensPage(CONFIG.getBaseURL());
    }

    @Test
    public void banner() {
        userPromo.triesToNoticeBanner();
        user.shouldSeeElementMatchingTo(mainPage.banner.flashParam,
                hasAttribute(VALUE, matches(AWAPS_HREF_PATTERN)));
        user.shouldSeeElementMatchingTo(mainPage.banner.movieParam,
                hasAttribute(VALUE, matches(AWAPS_HREF_PATTERN)));
    }
}