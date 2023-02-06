package ru.yandex.autotests.mainmorda.widgettests.wsettings;

import org.junit.Before;
import org.junit.Ignore;
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
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static ru.yandex.autotests.mainmorda.data.TvSettingsData.DEFAULT_TV_ITEMS_NUMBER;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;

/**
 * User: eoff
 * Date: 13.12.12
 */
@Aqua.Test(title = "Настройки ТВ")
@Features({"Main", "Widget", "Widget Settings"})
@Stories("Tv")
public class TvSettingsTest {
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
    @Ignore
    public void checkDefaultSettings() {
        user.shouldSeeElement(mainPage.tvSettings.selectChannelsToRemove);
        user.shouldSeeSelectWithSize(mainPage.tvSettings.selectChannelsToRemove,
                greaterThanOrEqualTo(TvSettingsData.DEFAULT_CHANNELS_CHOSEN_SIZE));
        user.shouldSeeElement(mainPage.tvSettings.autoReloadCheckbox);
        user.shouldSeeElementIsSelected(mainPage.tvSettings.autoReloadCheckbox);
        user.shouldSeeElement(mainPage.tvSettings.nightTVCheckbox);
        user.shouldSeeElementIsNotSelected(mainPage.tvSettings.nightTVCheckbox);
        user.shouldSeeElement(mainPage.tvSettings.selectProgrammeLength);
        userTvAfisha.shouldSeeSelectProgramLength();
    }

    @Test
    public void programSize5Default() {
        userTvAfisha.setChannelsCount(0);
        user.shouldSeeElement(mainPage.tvBlock);
        user.shouldSeeListWithSize(mainPage.tvBlock.tvEvents, equalTo(DEFAULT_TV_ITEMS_NUMBER));
        userMode.saveSettings();
        user.shouldSeePage(CONFIG.getBaseURL());
        user.shouldSeeElement(mainPage.tvBlock);
        user.shouldSeeListWithSize(mainPage.tvBlock.tvEvents, equalTo(DEFAULT_TV_ITEMS_NUMBER));
    }

    @Test
    @Ignore
    public void programSize5() {
        userTvAfisha.setChannelsCount(0);
        user.shouldSeeElement(mainPage.tvBlock);
        user.shouldSeeListWithSize(mainPage.tvBlock.tvEvents, equalTo(5));
        userMode.saveSettings();
        user.shouldSeePage(CONFIG.getBaseURL());
        user.shouldSeeElement(mainPage.tvBlock);
        user.shouldSeeListWithSize(mainPage.tvBlock.tvEvents, equalTo(5));
    }


    @Test
    @Ignore
    public void programSize7() {
        userTvAfisha.setChannelsCount(1);
        user.shouldSeeElement(mainPage.tvBlock);
        user.shouldSeeListWithSize(mainPage.tvBlock.tvEvents, equalTo(7));
        userMode.saveSettings();
        user.shouldSeePage(CONFIG.getBaseURL());
        user.shouldSeeElement(mainPage.tvBlock);
        user.shouldSeeListWithSize(mainPage.tvBlock.tvEvents, equalTo(7));

    }

    @Test
    @Ignore
    public void programSize10() {
        userTvAfisha.setChannelsCount(2);
        user.shouldSeeElement(mainPage.tvBlock);
        user.shouldSeeListWithSize(mainPage.tvBlock.tvEvents, equalTo(10));
        userMode.saveSettings();
        user.shouldSeePage(CONFIG.getBaseURL());
        user.shouldSeeElement(mainPage.tvBlock);
        user.shouldSeeListWithSize(mainPage.tvBlock.tvEvents, equalTo(10));
    }

    @Test
    @Ignore
    public void checkBoxSave() {
        user.shouldSeeElement(mainPage.tvSettings.nightTVCheckbox);
        user.selectElement(mainPage.tvSettings.nightTVCheckbox);
        user.shouldSeeElement(mainPage.tvSettings.okButton);
        user.clicksOn(mainPage.tvSettings.okButton);
        user.shouldNotSeeElement(mainPage.widgetSettings);
        user.shouldSeeElement(mainPage.tvBlock.editIcon);
        user.clicksOn(mainPage.tvBlock.editIcon);
        user.shouldSeeElement(mainPage.tvSettings.nightTVCheckbox);
        user.shouldSeeElementIsSelected(mainPage.tvSettings.nightTVCheckbox);
        user.deselectElement(mainPage.tvSettings.nightTVCheckbox);
        user.shouldSeeElement(mainPage.tvSettings.okButton);
        user.clicksOn(mainPage.tvSettings.okButton);
        user.shouldNotSeeElement(mainPage.widgetSettings);
        user.shouldSeeElement(mainPage.tvBlock.editIcon);
        user.clicksOn(mainPage.tvBlock.editIcon);
        user.shouldSeeElement(mainPage.tvSettings.nightTVCheckbox);
        user.shouldSeeElementIsNotSelected(mainPage.tvSettings.nightTVCheckbox);
    }

    @Test
    @Ignore
    public void selectAllButtons() {
        user.shouldSeeElement(mainPage.tvSettings.selectChannelsToAdd);
        user.shouldSeeElement(mainPage.tvSettings.selectChannelsToRemove);
        int beforeNew = mainPage.tvSettings.selectChannelsToAdd.getOptions().size();
        int beforeOld = mainPage.tvSettings.selectChannelsToRemove.getOptions().size();
        user.shouldSeeElement(mainPage.tvSettings.addAllChannelsButton);
        user.clicksOn(mainPage.tvSettings.addAllChannelsButton);
        user.shouldSeeSelectWithSize(mainPage.tvSettings.selectChannelsToRemove,
                equalTo(beforeNew + beforeOld));
        user.shouldSeeSelectWithSize(mainPage.tvSettings.selectChannelsToAdd,
                equalTo(0));
        user.shouldSeeElement(mainPage.tvSettings.removeAllChannelsButton);
        user.clicksOn(mainPage.tvSettings.removeAllChannelsButton);
        user.shouldSeeSelectWithSize(mainPage.tvSettings.selectChannelsToRemove,
                equalTo(1));
        user.shouldSeeSelectWithSize(mainPage.tvSettings.selectChannelsToAdd,
                equalTo(beforeNew + beforeOld - 1));
    }

    @Test
    @Ignore
    public void addChannel() {
        user.shouldSeeElement(mainPage.tvSettings.removeAllChannelsButton);
        user.clicksOn(mainPage.tvSettings.removeAllChannelsButton);
        user.shouldSeeElement(mainPage.tvSettings.selectChannelsToAdd);
        user.selectRandomOption(mainPage.tvSettings.selectChannelsToAdd);
        String channel = mainPage.tvSettings.selectChannelsToAdd.getFirstSelectedOption().getText();
        user.shouldSeeElement(mainPage.tvSettings.addOneChannelButton);
        user.clicksOn(mainPage.tvSettings.addOneChannelButton);
        user.shouldSeeElement(mainPage.tvSettings.selectChannelsToRemove);
        user.selectOption(mainPage.tvSettings.selectChannelsToRemove, 0);
        user.shouldSeeElement(mainPage.tvSettings.removeOneChannelButton);
        user.clicksOn(mainPage.tvSettings.removeOneChannelButton);
        user.shouldSeeElement(mainPage.tvSettings.okButton);
        user.clicksOn(mainPage.tvSettings.okButton);
        user.shouldNotSeeElement(mainPage.widgetSettings);
        user.shouldSeeElement(mainPage.widgetSettingsHeader);
        userMode.saveSettings();
        user.shouldSeeElement(mainPage.tvBlock);
        userTvAfisha.shouldSeeChannelProgram(channel);
    }
}
