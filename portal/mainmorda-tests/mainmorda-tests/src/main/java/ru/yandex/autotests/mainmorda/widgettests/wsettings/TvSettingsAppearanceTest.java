package ru.yandex.autotests.mainmorda.widgettests.wsettings;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.TvSettingsData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.TvAfishaSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;

/**
 * User: eoff
 * Date: 14.12.12
 */
@Aqua.Test(title = "Внешний вид настроек ТВ")
@Features({"Main", "Widget", "Widget Settings"})
@Stories("Tv")
public class TvSettingsAppearanceTest {
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
        userMode.setMode(WIDGET, mordaAllureBaseRule);
        userMode.setEditMode(CONFIG.getBaseURL());
        user.shouldSeeElement(mainPage.tvBlock);
        user.clicksOn(mainPage.tvBlock.editIcon);
        user.shouldSeeElement(mainPage.tvSettings);
    }

    @Test
    public void buttonsTexts() {
        user.shouldSeeElementMatchingTo(mainPage.tvSettings.addAllChannelsButton,
                hasAttribute(HtmlAttribute.VALUE, TvSettingsData.ADD_ALL_TEXT));
        user.shouldSeeElementMatchingTo(mainPage.tvSettings.addOneChannelButton,
                hasAttribute(HtmlAttribute.VALUE, TvSettingsData.ADD_TEXT));
        user.shouldSeeElementMatchingTo(mainPage.tvSettings.removeAllChannelsButton,
                hasAttribute(HtmlAttribute.VALUE, TvSettingsData.REMOVE_ALL_TEXT));
        user.shouldSeeElementMatchingTo(mainPage.tvSettings.removeOneChannelButton,
                hasAttribute(HtmlAttribute.VALUE, TvSettingsData.REMOVE_TEXT));
    }

    @Test
    public void tvChannelsText() {
        user.shouldSeeElement(mainPage.tvSettings.tvChannelsTitle);
        userTvAfisha.shouldSeeTvTitle(TvSettingsData.TV_TITLE_TEXT);
    }

    @Test
    public void tvQuantityText() {
        user.shouldSeeElement(mainPage.tvSettings.programmeLengthLabel);
        user.shouldSeeElementWithText(mainPage.tvSettings.programmeLengthLabel,
                TvSettingsData.TV_COUNT_TEXT);
    }

    @Test
    public void tvNoAnnouncesCheckBox() {
        user.shouldSeeElement(mainPage.tvSettings.nightTVCheckbox);
        user.shouldSeeElementWithText(mainPage.tvSettings.nightTVCheckbox,
                TvSettingsData.TV_NO_ANNOUNCE_TEXT);
    }

    @Test
    public void programLengthText() {
        user.shouldSeeElement(mainPage.tvSettings.programmeLengthLabel);
        user.shouldSeeElementWithText(mainPage.tvSettings.nightTVCheckbox,
                TvSettingsData.TV_NO_ANNOUNCE_TEXT);
    }

    @Test
    public void programLengthOptionsText() {
        userTvAfisha.shouldSeeCorrectChannelsOptionsText();
    }
}
