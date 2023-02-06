package ru.yandex.autotests.morda.tests.web.widgets.settings;

import org.junit.Before;
import org.junit.Rule;
import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainPage;
import ru.yandex.autotests.morda.pages.desktop.main.blocks.EtrainsBlock;
import ru.yandex.autotests.morda.pages.desktop.main.blocks.EtrainsSettingsBlock;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.region.Region;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;

import static ru.yandex.autotests.morda.steps.NavigationSteps.open;

/**
 * Created by asamar on 18.01.16.
 */
public class EtrainsSettingsTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private DesktopMainMorda morda;
    private WebDriver driver;
    private CommonMordaSteps user;
    private DesktopMainPage page;

    public EtrainsSettingsTest() {
        this.morda = DesktopMainMorda.desktopMain(CONFIG.getMordaScheme(), CONFIG.getMordaEnvironment(), Region.MOSCOW);
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.page = morda.getPage(driver);
    }

    @Before
    public void initialize() {
        morda.initialize(driver);
        URI addUrl = UriBuilder.fromUri(morda.getEditUrl())
                .queryParam("add", "_etrains")
                .build();
        open(driver, addUrl);
    }

//    @Test
    public void etrainsSettingsAppearance(){
        user.shouldSeeElement(page.getEtrainsBlock().getSetupPopup());
    }

//    @Test
    public void canSteupWidget(){
        EtrainsBlock etrainsBlock = page.getEtrainsBlock();
        etrainsBlock.switchToIFrame(driver);
//        ((JavascriptExecutor)driver).executeScript("document=document.getElementById(\"wd-prefs-_etrains-2\").contentWindow.document");
        try {
            Thread.sleep(5000L);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        EtrainsSettingsBlock etrainsSettingsBlock = etrainsBlock.getSetupPopup();
        user.shouldSeeElement(etrainsSettingsBlock);
        user.shouldSeeElement(etrainsSettingsBlock.directionSelector);
//        etrainsSettingsBlock.selectOption(etrainsSettingsBlock.directionSelector, 2);
//        etrainsSettingsBlock.selectOption(etrainsSettingsBlock.fromStationSelector, 2);
//        etrainsSettingsBlock.selectOption(etrainsSettingsBlock.toStationSelectorSelector, 4);
//        etrainsSettingsBlock.selectOption(etrainsSettingsBlock.etrainsNumberSelector, 3);
//
//        etrainsSettingsBlock.save();
//        System.out.println();
    }

}
