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
import static ru.yandex.autotests.morda.tests.web.utils.WidgetSteps.rssBlockUrl;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;

/**
 * User: asamar
 * Date: 11.01.2016.
 */
@Aqua.Test(title = "Adding widget")
@Features({"Main", "Widget", "Adding"})
@Stories("Adding widget")
@RunWith(Parameterized.class)
public class AddWidgetTest {
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
    private DesktopMainPage page;
    private WidgetSteps widgetSteps;

    public AddWidgetTest(DesktopMainMorda morda) {
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
    }

    @Test
    public void addFromUrlInEditMode() {
        open(driver, rssBlockUrl(morda.getEditUrl()));

        RssBlock rssBlock = page.getRssBlock();
        widgetSteps.acceptAddition(rssBlock);

        page.getEditModeControls().saveSettings();
        widgetSteps.shouldSee(rssBlock.getId());
    }

    @Test
    public void removeAddedFromUrlInEditMode() {
        open(driver, rssBlockUrl(morda.getEditUrl()));

        RssBlock rssBlock = page.getRssBlock();
        String rssBlockId = rssBlock.getId();
        widgetSteps.cancelAddition(rssBlock);

        page.getEditModeControls().saveSettings();
        widgetSteps.shouldNotSee(rssBlockId);
    }

    @Test
    public void setupAddedFromUrlInEditMode() {
        open(driver, rssBlockUrl(morda.getEditUrl()));

        RssBlock rssBlock = page.getRssBlock();
        widgetSteps.acceptAddition(rssBlock);

        rssBlock.setup()
                .setBigHeight()
                .showTitleOnly(false)
                .save();
        user.shouldNotSeeElement(rssBlock.rssSettingsBlock);
        widgetSteps.shouldSee(rssBlock.getId());

        RssSettingsBlock lentaSettingsBlock = rssBlock.setup();

        lentaSettingsBlock.showTitleOnlyCheckBox.shouldNotBeChecked();
        lentaSettingsBlock.save();

        page.getEditModeControls().saveSettings();
        widgetSteps.shouldSee(rssBlock.getId());
    }

    @Test
    public void addFromUrlInPlainMode(){
        open(driver, rssBlockUrl(morda.getUrl()));

        RssBlock rssBlock = page.getRssBlock();
        widgetSteps.acceptAddition(rssBlock);
    }

    @Test
    public void removeAddedFromUrlInPlainMode() throws InterruptedException {
        open(driver, rssBlockUrl(morda.getUrl()));

        RssBlock rssBlock = page.getRssBlock();
        String rssBlockId = rssBlock.getId();
        widgetSteps.acceptAddition(rssBlock);

        open(driver, morda.getEditUrl());
        rssBlock.widgetControls.removeWidget();
        widgetSteps.shouldNotSee(rssBlockId);

        page.getEditModeControls().saveSettings();
        widgetSteps.shouldNotSee(rssBlockId);
    }
}
