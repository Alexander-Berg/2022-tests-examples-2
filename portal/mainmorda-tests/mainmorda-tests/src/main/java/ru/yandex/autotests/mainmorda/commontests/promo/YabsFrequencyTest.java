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
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.Header;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.HeaderAction;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.Collections;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
@Aqua.Test(title = "Тест куки yabs-frequency")
@Features({"Main", "Common", "YabsFrequency"})
public class YabsFrequencyTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule()
            .mergeProxyAction(HeaderAction.class, Collections.singleton(new Header("X-Forwarded-For", "77.88.4.139")));

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private PromoSteps userPromo = new PromoSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void initLanguage() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
    }

    @Test
    public void yabsFrequencyCookieExists() {
        userPromo.shouldSeeYabsFrequencyCookie();
    }
}
