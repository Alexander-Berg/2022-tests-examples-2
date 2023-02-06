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

import static ru.yandex.autotests.morda.pages.desktop.main.blocks.RssSettingsBlock.ViewType.JOURNAL;
import static ru.yandex.autotests.morda.pages.desktop.main.blocks.RssSettingsBlock.ViewType.RANDOM_TEXT;
import static ru.yandex.autotests.morda.pages.desktop.main.blocks.RssSettingsBlock.ViewType.STANDART;
import static ru.yandex.autotests.morda.pages.desktop.main.blocks.RssSettingsBlock.ViewType.STANDART_WITH_PHOTO;
import static ru.yandex.autotests.morda.pages.desktop.main.blocks.RssSettingsBlock.WidgetHeqght.BIG;
import static ru.yandex.autotests.morda.steps.NavigationSteps.open;
import static ru.yandex.autotests.morda.tests.web.utils.WidgetSteps.militaryReviewUrl;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;

/**
 * User: asamar
 * Date: 15.01.2016.
 */
@Aqua.Test(title = "Настройки виджета рсс ленты")
@Features({"Main", "Widget", "Settings"})
@Stories("Rss")
@RunWith(Parameterized.class)
public class RssSettingsTest {
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

    public RssSettingsTest(DesktopMainMorda morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.widgetSteps = new WidgetSteps(driver);
        this.user = new CommonMordaSteps(driver);
        this.page = morda.getPage(driver);
    }

    @Before
    public void initialize() {
        morda.initialize(driver);
        open(driver, militaryReviewUrl(morda.getEditUrl()));
        widgetSteps.acceptAddition(page.getRssBlock());
    }

    @Test
    public void defaultView(){
        RssSettingsBlock rssSettingsBlock = page.getRssBlock().setup();
        rssSettingsBlock.shouldHaveView(STANDART_WITH_PHOTO);
        rssSettingsBlock.showTitleOnlyCheckBox.shouldBeChecked();
    }

    @Test
    public void headersOnly(){
        RssBlock rssBlock = page.getRssBlock();
        rssBlock.setup()
                .showTitleOnly(false)
                .save();

        user.shouldNotSeeElement(rssBlock.rssSettingsBlock);

        RssSettingsBlock rssSettingsBlock = rssBlock.setup();

        rssSettingsBlock.showTitleOnlyCheckBox.shouldNotBeChecked();

        rssBlock.setup()
                .showTitleOnly(true)
                .save();

        user.shouldNotSeeElement(rssSettingsBlock);

        rssBlock.setup()
                .showTitleOnlyCheckBox.shouldBeChecked();
    }

    @Test
    public void setBigHeight(){
        RssBlock rssBlock = page.getRssBlock();
        rssBlock.setup()
                .setBigHeight()
                .save();

        user.shouldNotSeeElement(rssBlock.rssSettingsBlock);

        RssSettingsBlock rssSettingsBlock = rssBlock.setup();

        rssSettingsBlock.shouldHaveHeight(BIG);
    }

    @Test
    public void setJournalView(){
        RssBlock rssBlock = page.getRssBlock();
        rssBlock.setup()
                .setJournalView()
                .save();
        user.shouldNotSeeElement(rssBlock.rssSettingsBlock);

        rssBlock.setup()
                .shouldHaveView(JOURNAL);
    }

    @Test
    public void setStandartView(){
        RssBlock rssBlock = page.getRssBlock();
        rssBlock.setup()
                .setStandartView()
                .save();

        user.shouldNotSeeElement(rssBlock.rssSettingsBlock);

        rssBlock.setup().shouldHaveView(STANDART);
    }

    @Test
    public void setRandomTestView(){
        RssBlock rssBlock = page.getRssBlock();
        rssBlock.setup()
                .setRandomTextView()
                .save();
        user.shouldNotSeeElement(rssBlock.rssSettingsBlock);

        rssBlock.setup()
                .shouldHaveView(RANDOM_TEXT);
    }
}
