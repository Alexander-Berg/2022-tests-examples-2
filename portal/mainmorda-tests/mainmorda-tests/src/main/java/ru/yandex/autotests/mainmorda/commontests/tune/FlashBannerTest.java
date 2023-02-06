package ru.yandex.autotests.mainmorda.commontests.tune;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.TuneData;
import ru.yandex.autotests.mainmorda.pages.TuneBannerPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.PromoSteps;
import ru.yandex.autotests.mainmorda.steps.TuneSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static org.hamcrest.Matchers.is;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;

/**
 * User: eoff
 * Date: 01.02.13
 */
@Aqua.Test(title = "Отключение баннера")
@Features({"Main", "Common", "Banner"})
@Stories("Turn Off")
public class FlashBannerTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private TuneSteps userTune = new TuneSteps(driver);
    private PromoSteps userPromo = new PromoSteps(driver);
    private TuneBannerPage tuneBannerPage = new TuneBannerPage(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        user.opensPage("http://awaps.yandex.ru/?adt_id=82599");
        userPromo.shouldSeeAdtIdOnAwapsPage("82599");
        user.opensPage(CONFIG.getBaseURL());
    }

    @Test
    public void bannerTurnsOff() {
        assumeThat(CONFIG.domainIs(RU), is(true));
        userTune.shouldSeeBanner();
        user.opensPage(TuneData.TUNE_BANNER_URL);
        user.selectElement(tuneBannerPage.noBannerCheckbox);
        user.clicksOn(tuneBannerPage.saveButton);
        user.shouldSeePage(CONFIG.getBaseURL());
        userTune.shouldNotSeeBanner();
        user.opensPage(TuneData.TUNE_BANNER_URL);
        user.deselectElement(tuneBannerPage.noBannerCheckbox);
        user.clicksOn(tuneBannerPage.saveButton);
        user.shouldSeePage(CONFIG.getBaseURL());
        userTune.shouldSeeBanner();
    }
}
