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
import ru.yandex.autotests.morda.pages.desktop.main.blocks.TvBlock;
import ru.yandex.autotests.morda.pages.desktop.main.blocks.TvSettingsBlock;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.Widget;
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
 * User: eoff (eoff@yandex-team.ru)
 * Date: 29/11/15
 */
@Aqua.Test(title = "Deleting widget")
@Features({"Main", "Widget", "Deleting"})
@Stories("Deleting widget")
@RunWith(Parameterized.class)
public class DeleteWidgetTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<DesktopMainMorda> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();

        data.addAll(DesktopMainMorda.getDefaultList(scheme, environment));
//        data.add(desktopMain(scheme, environment, MOSCOW));
        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private DesktopMainMorda morda;
    private WebDriver driver;
    private CommonMordaSteps user;
    private WidgetSteps widgetSteps;
    private DesktopMainPage page;

    public DeleteWidgetTest(DesktopMainMorda morda) {
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
    public void canRemoveWidget() throws InterruptedException {
        Widget randomWidget = widgetSteps.getRandomWidget();
        String randomWidgetId = randomWidget.getId();

        randomWidget.widgetControls.removeWidget();
        widgetSteps.shouldNotSee(randomWidgetId);

        page.getEditModeControls().saveSettings();
        widgetSteps.shouldNotSee(randomWidgetId);
    }

    @Test
    public void canReturnWidget() throws InterruptedException {
        Widget randomWidget = widgetSteps.getRandomWidget();
        String randomWidgetId = randomWidget.getId();

        randomWidget.widgetControls.removeWidget();
        widgetSteps.shouldNotSee(randomWidgetId);

        page.getEditModeControls().undoDeletion();
        widgetSteps.shouldSee(randomWidgetId);

        page.getEditModeControls().saveSettings();
        widgetSteps.shouldSee(randomWidgetId.replace("-1", ""));
    }

    @Test
    public void canRemoveTwoWidgets() throws InterruptedException {
        Widget randomWidget1 = widgetSteps.getRandomWidget();
        String randomWidget1Id = randomWidget1.getId();
        randomWidget1.widgetControls.removeWidget();
        widgetSteps.shouldNotSee(randomWidget1Id);

        Widget randomWidget2 = widgetSteps.getRandomWidget();
        String randomWidget2Id = randomWidget2.getId();
        randomWidget2.widgetControls.removeWidget();
        widgetSteps.shouldNotSee(randomWidget2Id);

        page.getEditModeControls().saveSettings();
        widgetSteps.shouldNotSee(randomWidget1Id);
        widgetSteps.shouldNotSee(randomWidget2Id);
    }

    @Test
    public void canReturnTwoWidgets() throws InterruptedException {
        Widget randomWidget1 = widgetSteps.getRandomWidget();
        String randomWidget1Id = randomWidget1.getId();
        randomWidget1.widgetControls.removeWidget();
        widgetSteps.shouldNotSee(randomWidget1Id);

        Widget randomWidget2 = widgetSteps.getRandomWidget();
        String randomWidget2Id = randomWidget2.getId();
        randomWidget2.widgetControls.removeWidget();
        widgetSteps.shouldNotSee(randomWidget2Id);

        page.getEditModeControls().undoDeletion();
        page.getEditModeControls().undoDeletion();
        widgetSteps.shouldSee(randomWidget1Id);
        widgetSteps.shouldSee(randomWidget2Id);

        page.getEditModeControls().saveSettings();
        widgetSteps.shouldSee(randomWidget1Id.replace("-1", ""));
        widgetSteps.shouldSee(randomWidget2Id.replace("-1", ""));
    }

    @Test
    public void canReturnOneOfTwoWidgets() throws InterruptedException {
        Widget randomWidget1 = widgetSteps.getRandomWidget();
        String randomWidget1Id = randomWidget1.getId();
        randomWidget1.widgetControls.removeWidget();
        widgetSteps.shouldNotSee(randomWidget1Id);

        Widget randomWidget2 = widgetSteps.getRandomWidget();
        String randomWidget2Id = randomWidget2.getId();
        randomWidget2.widgetControls.removeWidget();
        widgetSteps.shouldNotSee(randomWidget2Id);

        page.getEditModeControls().undoDeletion();
        widgetSteps.shouldNotSee(randomWidget1Id);
        widgetSteps.shouldSee(randomWidget2Id);

        page.getEditModeControls().saveSettings();
        widgetSteps.shouldNotSee(randomWidget1Id);
        widgetSteps.shouldSee(randomWidget2Id);
    }

    @Test
    public void canReturnAddedWidget() throws InterruptedException {
        open(driver, rssBlockUrl(morda.getEditUrl()));

        RssBlock widgetBeingAdded = page.getRssBlock();
        String addedWidgetId = widgetBeingAdded.getId();
        widgetSteps.acceptAddition(widgetBeingAdded);

        widgetBeingAdded.widgetControls.removeWidget();
        widgetSteps.shouldNotSee(addedWidgetId);

        page.getEditModeControls().undoDeletion();
        widgetSteps.shouldSee(addedWidgetId);

        page.getEditModeControls().saveSettings();
        widgetSteps.shouldSee(addedWidgetId);
    }

    @Test
    public void canSetupWidget() throws InterruptedException {

        TvBlock tvBlock = page.getTvBlock();

        tvBlock.setup()
                .eveningMode(true)
                .autoUpdate(false)
                .selectChannelsById("53")
                .save();

        user.shouldNotSeeElement(tvBlock.tvSettingsBlock);

        tvBlock.widgetControls.removeWidget();
        user.shouldNotSeeElement(tvBlock);

        page.getEditModeControls().undoDeletion();
        user.shouldSeeElement(tvBlock);

        TvSettingsBlock tvSettingsBlock = tvBlock.setup();
        tvSettingsBlock.eveningMode.shouldBeChecked();
        tvSettingsBlock.autoUpdate.shouldNotBeChecked();
        tvSettingsBlock.save();

        page.getEditModeControls().saveSettings();
        user.shouldSeeElement(tvBlock);
    }

    @Test
    public void canAddAndSetupWidget() {
        open(driver, rssBlockUrl(morda.getEditUrl()));

        RssBlock lentaBlock = page.getRssBlock();
        widgetSteps.acceptAddition(lentaBlock);

        lentaBlock.setup()
                .setBigHeight()
                .showTitleOnly(false)
                .save();
        user.shouldNotSeeElement(lentaBlock.rssSettingsBlock);

        lentaBlock.widgetControls.removeWidget();
        user.shouldNotSeeElement(lentaBlock);

        page.getEditModeControls().undoDeletion();
        user.shouldSeeElement(lentaBlock);

        RssSettingsBlock lentaSettingsBlock = lentaBlock.setup();

        lentaSettingsBlock.showTitleOnlyCheckBox.shouldNotBeChecked();
        lentaSettingsBlock.save();

        page.getEditModeControls().saveSettings();
        user.shouldSeeElement(lentaBlock);
    }
}
