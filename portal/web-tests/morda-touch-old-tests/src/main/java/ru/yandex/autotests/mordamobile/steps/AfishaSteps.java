package ru.yandex.autotests.mordamobile.steps;

//import ru.yandex.qatools.allure.annotations.Step;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.Matchers.isIn;
import static ru.yandex.autotests.mordamobile.blocks.AfishaBlock.AfishaEvent;
import static ru.yandex.autotests.mordamobile.data.AfishaData.AFISHA_LINK;
import static ru.yandex.autotests.mordamobile.data.AfishaData.GENRES;
import static ru.yandex.qatools.htmlelements.matchers.common.HasTextMatcher.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
public class AfishaSteps {
    private static final Properties CONFIG = new Properties();

    private WebDriver driver;
    private HomePage homePage;
    public CommonMordaSteps userSteps;

    public AfishaSteps(WebDriver driver) {
        this.driver = driver;
        userSteps = new CommonMordaSteps(driver);
        homePage = new HomePage(driver);
    }

    @Step
    public void shouldSeeAfishaLinks() {
        for (int i = 0; i < homePage.afishaBlock.allEvents.size(); i++) {
            HtmlElement element = homePage.afishaBlock.allEvents.get(i);
            userSteps.shouldSeeLink(element, AFISHA_LINK);
            userSteps.opensPage(CONFIG.getBaseURL());
        }
    }

    @Step
    public void shouldSeeAfishaGenres() {
        for (AfishaEvent event : homePage.afishaBlock.allEvents) {
            userSteps.shouldSeeElementMatchingTo(event.genre, hasText(isIn(GENRES)));
        }
    }
}
