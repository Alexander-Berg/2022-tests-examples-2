package ru.yandex.autotests.mordamobile.steps;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.blocks.TvBlock;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.mordamobile.data.TvData.TIME_MATCHER;
import static ru.yandex.autotests.mordamobile.data.TvData.getTvEventLink;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
public class TvSteps {
    private static final Properties CONFIG = new Properties();

    private WebDriver driver;
    private HomePage homePage;
    public CommonMordaSteps userSteps;

    public TvSteps(WebDriver driver) {
        this.driver = driver;
        userSteps = new CommonMordaSteps(driver);
        homePage = new HomePage(driver);
    }

    @Step
    public void shouldSeeTvLinks(Region region) {
        for (int i = 0; i < homePage.tvBlock.allEvents.size(); i++) {
            HtmlElement element = homePage.tvBlock.allEvents.get(i);
            userSteps.shouldSeeLink(element, getTvEventLink(region));
            userSteps.opensPage(CONFIG.getBaseURL());
        }
    }

    @Step
    public void shouldSeeTvEvents() {
        for (TvBlock.TvEvent event : homePage.tvBlock.allEvents) {
            userSteps.shouldSeeElement(event.time);
            userSteps.shouldSeeElementWithText(event.time, TIME_MATCHER);
            userSteps.shouldSeeElement(event.program);
            userSteps.shouldSeeElementWithText(event.program, not(""));
            userSteps.shouldSeeElementWithText(event, not(event.time.getText() + event.program.getText()));
        }
    }

}
