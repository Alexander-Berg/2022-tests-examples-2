package ru.yandex.autotests.mainmorda.commontests.tv;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.RatesData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.TvAfishaSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.Mode;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mainmorda.data.TVAfishaData.TV_ITEMS_NUMBER;
import static ru.yandex.autotests.utils.morda.url.Domain.KZ;

/**
 * User: alex89
 * Date: 28.02.13
 */
@Aqua.Test(title = "ТВ(вид по-умолчанию)")
@Features({"Main", "Common", "TV"})
@Stories("Default View")
public class TVDefaultViewTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private TvAfishaSteps userTvAfisha = new TvAfishaSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        user.shouldSeeElement(mainPage.tvBlock);
    }

    @Test
    public void tvTitle() {
        userTvAfisha.shouldSeeTvTitleLinkInWidget(mainPage.tvBlock);
    }

    @Test
    public void tvEventsInDefaultView() {
        user.shouldSeeListWithSize(mainPage.tvBlock.tvEvents, TV_ITEMS_NUMBER);
        userTvAfisha.shouldSeeDifferentTvEventsInWidget(mainPage.tvBlock);
        userTvAfisha.shouldSeeTvEventsTimeInWidget(mainPage.tvBlock);
        userTvAfisha.shouldSeeTvEventsLinksInWidget(mainPage.tvBlock);
    }
}
