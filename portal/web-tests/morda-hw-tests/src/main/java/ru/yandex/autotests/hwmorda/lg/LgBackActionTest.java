package ru.yandex.autotests.hwmorda.lg;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.hwmorda.Properties;
import ru.yandex.autotests.hwmorda.pages.LgSubPage;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static ru.yandex.autotests.hwmorda.data.LgRubricData.ALL_RUBRICS;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;


/**
 * User: alex89
 * Date: 12.09.12
 */
@Aqua.Test(title = "LG - проверка действий по переходу назад")
@RunWith(Parameterized.class)
@Features("LG")
@Stories("Back Action")
public class LgBackActionTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private LgSubPage lgSubPage = new LgSubPage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> testData() {
        return ParametrizationConverter.convert(ALL_RUBRICS);
    }

    private String fromUrl;

    public LgBackActionTest(String fromUrl) {
        this.fromUrl = fromUrl;
    }

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getLgBaseUrl());
        user.setsRegion(MOSCOW, CONFIG.getLgBaseUrl());
        user.opensPage(fromUrl);
        user.shouldSeeElement(lgSubPage.footerPanel);
    }

    @Test
    public void exitFooterButtonIsPresent() {
        user.shouldSeeElement(lgSubPage.footerPanel.exitButton);
        user.clicksOn(lgSubPage.footerPanel.exitButton);
        user.shouldSeePage(fromUrl);
    }

    @Test
    public void backFooterButtonActionIsCorrect() {
        user.shouldSeeElement(lgSubPage.footerPanel.backButton);
        user.clicksOn(lgSubPage.footerPanel.backButton);
        user.shouldSeePage(CONFIG.getLgBaseUrl());
    }

    @Test
    public void homeRubricButtonActionIsCorrect() {
        user.shouldSeeElement(lgSubPage.rubricsPanel.homeButton);
        user.clicksOn(lgSubPage.rubricsPanel.homeButton);
        user.shouldSeePage(CONFIG.getLgBaseUrl());
    }

    @Test
    public void logoActionIsCorrect() {
        user.shouldSeeElement(lgSubPage.logo);
        user.clicksOn(lgSubPage.logo);
        user.shouldSeePage(CONFIG.getLgBaseUrl());
    }
}