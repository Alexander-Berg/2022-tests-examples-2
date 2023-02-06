package ru.yandex.autotests.morda.tests.web.widgets.actions;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainPage;
import ru.yandex.autotests.morda.pages.desktop.main.blocks.RssBlock;
import ru.yandex.autotests.morda.pages.desktop.main.blocks.RssSettingsBlock;
import ru.yandex.autotests.morda.pages.desktop.main.blocks.TopnewsBlock;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.morda.tests.web.utils.WidgetSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.morda.steps.NavigationSteps.open;
import static ru.yandex.autotests.morda.tests.web.utils.WidgetSteps.militaryReviewUrl;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;

/**
 * User: asamar
 * Date: 02.08.16
 */
@Aqua.Test(title = "Reset settings")
@Features({"Main", "Widget", "Reset settings"})
@Stories("Reset settings")
@RunWith(Parameterized.class)
public class ResetSettingsTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<DesktopMainMorda> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();

        data.addAll(DesktopMainMorda.getDefaultList(scheme, environment));
        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private DesktopMainMorda morda;
    private WebDriver driver;
    private CommonMordaSteps user;
    private WidgetSteps widgetSteps;
    private DesktopMainPage page;

    public ResetSettingsTest(DesktopMainMorda morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.page = morda.getPage(driver);
        this.widgetSteps = new WidgetSteps(driver);
    }

    @Before
    public void initialize() {
        morda.initialize(driver);
        open(driver, morda.getEditUrl());
    }

    @Test
    public void resetSettingsDefaultWidgetFromEditMode() {
        TopnewsBlock topnewsBlock = page.getNewsBlock();

        topnewsBlock.setup()
                .showNumeration(false)
                .save();
        user.shouldNotSeeElement(topnewsBlock.topnewsSettingsBlock);
        widgetSteps.shouldNotSeeNumbers();

        topnewsBlock.setup().reset();
        user.shouldNotSeeElement(topnewsBlock.topnewsSettingsBlock);
        widgetSteps.shouldSeeNumbers();

        page.getEditModeControls().saveSettings();
        widgetSteps.shouldSeeNumbers();
    }


    @Test
    public void resetSettingsDefaultWidgetFromPlainMode() {
        TopnewsBlock topnewsBlock = page.getNewsBlock();

        topnewsBlock.setup()
                .showNumeration(false)
                .save();
        user.shouldNotSeeElement(topnewsBlock.topnewsSettingsBlock);
        widgetSteps.shouldNotSeeNumbers();

        page.getEditModeControls().saveSettings();
        open(driver, morda.getEditUrl());

        topnewsBlock.setup().reset();
        user.shouldNotSeeElement(topnewsBlock.topnewsSettingsBlock);
        widgetSteps.shouldSeeNumbers();

        page.getEditModeControls().saveSettings();
        widgetSteps.shouldSeeNumbers();
    }

    @Test
    public void resetSettingsRssWidgetFromEditMode() {
        open(driver, militaryReviewUrl(morda.getEditUrl()));
        RssBlock rssBlock = page.getRssBlock();
        widgetSteps.acceptAddition(rssBlock);

        rssBlock.setup()
                .showTitleOnly(false)
                .save();

        RssSettingsBlock rssSettingsBlock = rssBlock.setup();
        rssSettingsBlock.showTitleOnlyCheckBox.shouldNotBeChecked();
        rssSettingsBlock.reset();

        rssBlock.setup()
                .showTitleOnlyCheckBox.shouldBeChecked();
    }

    @Test
    public void resetSettingsRssWidgetFromPlainMode() {
        open(driver, militaryReviewUrl(morda.getEditUrl()));
        RssBlock rssBlock = page.getRssBlock();
        widgetSteps.acceptAddition(rssBlock);

        rssBlock.setup()
                .showTitleOnly(false)
                .save();

        page.getEditModeControls().saveSettings();
        open(driver, morda.getEditUrl());

        RssSettingsBlock rssSettingsBlock = rssBlock.setup();
        rssSettingsBlock.showTitleOnlyCheckBox.shouldNotBeChecked();
        rssSettingsBlock.reset();

        rssBlock.setup().showTitleOnlyCheckBox.shouldBeChecked();
    }
}
