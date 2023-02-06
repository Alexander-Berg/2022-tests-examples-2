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
import ru.yandex.autotests.morda.pages.desktop.main.blocks.RatesBlock;
import ru.yandex.autotests.morda.pages.desktop.main.blocks.RatesSettingsBlock;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.morda.pages.desktop.main.blocks.RatesSettingsBlock.DecimalPlacesType.FOUR;
import static ru.yandex.autotests.morda.steps.NavigationSteps.open;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;

/**
 * User: asamar
 * Date: 17.01.2016.
 */
@Aqua.Test(title = "Настройки виджета котировок")
@Features({"Main", "Widget", "Settings"})
@Stories("Rates")
@RunWith(Parameterized.class)
public class RatesSettingsTest {
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
    private RatesBlock ratesBlock;
    private RatesSettingsBlock ratesSettingsBlock;

    public RatesSettingsTest(DesktopMainMorda morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.page = morda.getPage(driver);
    }

    @Before
    public void initialize() throws InterruptedException {
        morda.initialize(driver);
        open(driver, morda.getEditUrl());
        page.getNewsBlock().setup()
                .showNumeration(false)
                .save();
        page.getEditModeControls().saveSettings();
        page.getNewsBlock().openQuotesBlock();
        ratesBlock = page.getRatesBlock();
        user.shouldSeeElement(ratesBlock);
        ratesSettingsBlock =  ratesBlock.setup();

    }

    @Test
    public void canCheckRatesAndDecimalPlaces() {
        ratesSettingsBlock
                .setFourSign()
                .selectQuotesById("24", "6", "42", "17", "20001", "10016", "10021")
                .save();
        user.shouldNotSeeElement(ratesBlock.ratesSettingsBlock);

        ratesBlock.shouldSeeQuotesByValue("24", "6", "42", "17", "20001", "10016", "10021");

        ratesBlock.setup()
                .shouldSeeDecimalPlaces(FOUR);
    }

    @Test
    public void canCheckAutoupdateAndMarkColor(){
        this.ratesSettingsBlock
                .autoUpdate(false)
                .colorMark(false)
                .save();
        user.shouldNotSeeElement(ratesBlock.ratesSettingsBlock);

        RatesSettingsBlock ratesSettingsBlock = ratesBlock.setup();

        ratesSettingsBlock.autoUpdate.shouldNotBeChecked();
        ratesSettingsBlock.markColor.shouldNotBeChecked();
    }
}
