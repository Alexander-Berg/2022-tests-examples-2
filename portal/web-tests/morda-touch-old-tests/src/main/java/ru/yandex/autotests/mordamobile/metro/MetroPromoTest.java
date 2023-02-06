package ru.yandex.autotests.mordamobile.metro;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.UserAgentAction;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.autotests.mordaexportsclient.beans.MetroTouchEntry;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;


import static org.hamcrest.Matchers.containsString;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.*;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.*;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.*;
import static ru.yandex.autotests.mordaexportslib.matchers.GeoMatcher.*;
import static ru.yandex.autotests.mordaexportslib.matchers.LangMatcher.*;

/**
 * User: Poluektov Evgeniy <poluektov@yandex-team.ru>
 * on: 24.12.2014.
 */
@Aqua.Test(title = "Блок метро")
@Features("Metro")
public class MetroPromoTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule()
            .replaceProxyAction(UserAgentAction.class,
                "Mozilla/5.0 (Linux; U; Android 4.0.3; de-ch; HTC Sensation Build/IML74K) " +
                        "AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30");


    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private HomePage homePage = new HomePage(driver);

    private final MetroTouchEntry ENTRY = export(METRO_TOUCH, domain(CONFIG.getBaseDomain()),
            lang(CONFIG.getLang()), geo(CONFIG.getBaseDomain().getCapital().getRegionIdInt()));

    @Before
    public void setUp(){
        user.initTest(CONFIG.getBaseURL(),CONFIG.getBaseDomain().getCapital(),CONFIG.getLang());
        user.shouldSeePage(CONFIG.getBaseURL());
    }

    @Test
    public void hasPromo() {
        user.shouldSeeElement(homePage.metroBlock);
    }

    @Test
    public void hasCorrectLink() {
        user.shouldSeeElementMatchingTo(homePage.metroBlock.metroLink,
                hasAttribute(HtmlAttribute.HREF, containsString(ENTRY.getUrl())));
    }

    @Test
    public void hasCorrectIcon() {
        user.shouldSeeElementMatchingTo(homePage.metroBlock.metroIcon,
                hasAttribute(HtmlAttribute.CLASS, containsString("b-metro__icon_city_" + ENTRY.getIcon())) );
    }

    @Test
    public void regionWithoutMetro() {
        user.setsRegion(Region.AMSTERDAM);
        user.shouldNotSeeElement(homePage.metroBlock);
    }
}
