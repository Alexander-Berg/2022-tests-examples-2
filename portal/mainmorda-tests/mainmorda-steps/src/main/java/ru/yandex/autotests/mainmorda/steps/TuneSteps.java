package ru.yandex.autotests.mainmorda.steps;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.data.TuneData;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.pages.TuneRegionPage;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static ru.yandex.qatools.htmlelements.matchers.common.DoesElementExistMatcher.exists;

/**
 * User: eoff
 * Date: 01.02.13
 */
public class TuneSteps {
    private static final Properties CONFIG = new Properties();

    private WebDriver driver;
    private CommonMordaSteps userSteps;
    private MainPage mainPage;
    private TuneRegionPage tuneRegionPage;

    public TuneSteps(WebDriver driver) {
        this.driver = driver;
        this.userSteps = new CommonMordaSteps(driver);
        this.mainPage = new MainPage(driver);
        this.tuneRegionPage = new TuneRegionPage(driver);
    }

    @Step
    public void setRegion(Domain currDomain, Domain newDomain) {
        userSteps.shouldSeeElement(mainPage.headerBlock);
        userSteps.shouldSeeElement(mainPage.headerBlock.setupLink);
        userSteps.clicksOn(mainPage.headerBlock.setupLink);
        userSteps.shouldSeeElement(mainPage.headerBlock.setupMainPopUp);
        userSteps.shouldSeeElement(mainPage.headerBlock.setupMainPopUp.changeCityLink);
        userSteps.clicksOn(mainPage.headerBlock.setupMainPopUp.changeCityLink);
        userSteps.shouldSeePage(TuneData.TUNE_URL_PATTERN.replace("%s", currDomain.toString()));
        userSteps.clearsInput(tuneRegionPage.input);
        userSteps.entersTextInInput(tuneRegionPage.input, newDomain.getCapital().getName());
        userSteps.shouldSeeElement(tuneRegionPage.suggest);
        userSteps.clicksOn(tuneRegionPage.suggest);
        userSteps.shouldSeePage(String.format(TuneData.YANDEX_URL_PATTERN, newDomain));
    }

    @Step
    public void shouldSeeBanner() {
        assertTrue("Баннер не виден", isBannerPresent());
    }

    @Step
    public void shouldNotSeeBanner() {
        assertFalse("Баннер виден", isBannerPresent());
    }

    public boolean isBannerPresent() {
        for (int i = 0; i < 5; i++) {
            driver.navigate().refresh();
            HtmlElement banner = mainPage.banner;
            if (bannerPresent(banner)) {
                return true;
            }
        }
        return false;
    }

    private boolean bannerPresent(HtmlElement banner) {
        return exists().matches(banner) && banner.isDisplayed();
    }
}
