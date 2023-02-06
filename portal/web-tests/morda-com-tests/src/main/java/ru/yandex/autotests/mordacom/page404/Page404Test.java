package ru.yandex.autotests.mordacom.page404;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacom.Properties;
import ru.yandex.autotests.mordacom.pages.Page404;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mordacom.data.Page404Data.COMPANY_LINK;
import static ru.yandex.autotests.mordacom.data.Page404Data.FEEDBACK_MESSAGE;
import static ru.yandex.autotests.mordacom.data.Page404Data.FEEDBACK_URL;
import static ru.yandex.autotests.mordacom.data.Page404Data.NO_PAGE_TEXT;
import static ru.yandex.autotests.mordacom.data.Page404Data.PAGE_404_URL;
import static ru.yandex.autotests.mordacom.data.Page404Data.REQUEST;
import static ru.yandex.autotests.mordacom.data.Page404Data.SEARCH_BUTTON_TEXT_MATCHER;
import static ru.yandex.autotests.mordacom.data.Page404Data.SEARCH_URL;
import static ru.yandex.autotests.mordacom.data.Page404Data.YANDEX_LINK;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;

/**
 * User: eoff
 * Date: 07.02.13
 */
@Aqua.Test(title = "Страница 404")
@Features("Page 404")
@Stories("Content")
public class Page404Test {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private Page404 page404 = new Page404(driver);

    @Before
    public void setUp() {
        user.opensPage(PAGE_404_URL);
    }

    @Test
    public void searchButton() {
        user.shouldSeeElement(page404.searchButton);
        user.shouldSeeElementWithText(page404.searchButton, SEARCH_BUTTON_TEXT_MATCHER);
        user.shouldSeeElement(page404.input);
        user.entersTextInInput(page404.input, REQUEST);
        user.clicksOn(page404.searchButton);
        user.shouldSeePage(SEARCH_URL);
    }

    @Test
    public void yandexLogo() {
        user.shouldSeeElement(page404.logo);
    }

    @Test
    public void noPageText() {
        user.shouldSeeElement(page404.errorMessage);
        user.shouldSeeElementWithText(page404.errorMessage, NO_PAGE_TEXT);
    }

    @Test
    public void feedbackText() {
        user.shouldSeeElement(page404.feedbackMessage);
        user.shouldSeeElementWithText(page404.feedbackMessage, FEEDBACK_MESSAGE);
        user.shouldSeeElement(page404.feedbackLink);
        user.shouldSeeElementMatchingTo(page404.feedbackLink, hasAttribute(HREF, FEEDBACK_URL));
    }

    @Test
    public void companyLink() {
        user.shouldSeeLink(page404.companyLink, COMPANY_LINK);
    }

    @Test
    public void yandexLink() {
        user.shouldSeeLink(page404.yandexLink, YANDEX_LINK);
    }
}
