package ru.yandex.autotests.mainmorda.commontests.promo;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.PromoSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mainmorda.data.PromoData.AWAPS_HREF_PATTERN;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.STYLE;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.VALUE;

/**
 * User: alex89
 * Date: 09.04.12
 */
@Aqua.Test(title = "Появление вертикального баннера и параметры")
@Features({"Main", "Common", "Banner"})
public class VerticalBannerTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule(DesiredCapabilities.chrome());

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private PromoSteps userPromo = new PromoSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void initLanguage() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        user.resizeWindow(1336, 1024);
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        user.opensPage("http://awaps.yandex.ru/?adt_id=358510");
        userPromo.shouldSeeAdtIdOnAwapsPage("358510");
        user.opensPage(CONFIG.getBaseURL());
    }

    @Test
    public void verticalBanner() {
        userPromo.triesToNoticeVerticalBanner();
        user.shouldSeeElementMatchingTo(mainPage.verticalBanner.flashParam,
                hasAttribute(VALUE, matches(AWAPS_HREF_PATTERN)));
    }

    @Test
    public void verticalBannerActions() {
        userPromo.triesToNoticeVerticalBanner();
        user.shouldSeeElement(mainPage.logotype);
        user.shouldSeeElement(mainPage.verticalBanner);
        user.clicksOn(mainPage.verticalBanner);
        user.shouldSeeElementMatchingTo(mainPage.verticalBanner, hasAttribute(STYLE, equalTo("width: 900px;")));
    }
}