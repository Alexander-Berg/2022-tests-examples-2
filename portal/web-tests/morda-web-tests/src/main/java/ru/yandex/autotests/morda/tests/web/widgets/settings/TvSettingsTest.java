package ru.yandex.autotests.morda.tests.web.widgets.settings;

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
import ru.yandex.autotests.morda.pages.desktop.main.blocks.TvBlock;
import ru.yandex.autotests.morda.pages.desktop.main.blocks.TvSettingsBlock;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.morda.tests.web.utils.WidgetSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.hamcrest.Matchers.lessThanOrEqualTo;
import static ru.yandex.autotests.morda.steps.NavigationSteps.open;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 29/11/15
 */
@Aqua.Test(title = "Настройки виджета ТВ")
@Features({"Main", "Widget", "Settings"})
@Stories("Tv")
@RunWith(Parameterized.class)
public class TvSettingsTest {
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

    public TvSettingsTest(DesktopMainMorda morda) {
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
    public void canSetupWidget() throws InterruptedException {
        TvBlock tvBlock = page.getTvBlock();
        tvBlock.setup()
                .eveningMode(true)
                .autoUpdate(false)
                .groupByChannel(true)
                .selectChannelsById("737")
                .save();

        user.shouldNotSeeElement(tvBlock.tvSettingsBlock);

        TvSettingsBlock tvSettingsBlock = tvBlock.setup();

        tvSettingsBlock.getChannelById("737").shouldBeChecked();
        tvSettingsBlock.eveningMode.shouldBeChecked();
        tvSettingsBlock.groupByChannels.shouldBeChecked();
        tvSettingsBlock.autoUpdate.shouldNotBeChecked();
        tvSettingsBlock.close();

        page.getEditModeControls().saveSettings();
        widgetSteps.shouldSee(tvBlock.getId());
    }

    @Test
    public void setChannelsCount() {
        TvBlock tvBlock = page.getTvBlock();
        tvBlock.setup()
                .sevenChannels()
                .save();

        user.shouldNotSeeElement(tvBlock.tvSettingsBlock);
        user.shouldSeeListWithSize(tvBlock.tvEvents, lessThanOrEqualTo(7));

        tvBlock.setup()
                .tenChannels()
                .save();

        user.shouldNotSeeElement(tvBlock.tvSettingsBlock);
        user.shouldSeeListWithSize(tvBlock.tvEvents, lessThanOrEqualTo(10));

        page.getEditModeControls().saveSettings();
        user.shouldSeeListWithSize(tvBlock.tvEvents, lessThanOrEqualTo(10));
    }
}
