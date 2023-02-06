package ru.yandex.autotests.mainmorda.plaintests.page404;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.Page404;
import ru.yandex.autotests.mainmorda.steps.LinksSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import static ru.yandex.autotests.mainmorda.blocks.PageBlock.ALL_SERVICES;
import static ru.yandex.autotests.mainmorda.blocks.PageBlock.PAGE_404;
import static ru.yandex.autotests.mainmorda.data.Page404Data.COMPANY_COM_LINK;
import static ru.yandex.autotests.mainmorda.data.Page404Data.COMPANY_RU_LINK;
import static ru.yandex.autotests.mainmorda.data.Page404Data.FEEDBACK_URL;
import static ru.yandex.autotests.mainmorda.data.Page404Data.NO_PAGE_TEXT;
import static ru.yandex.autotests.mainmorda.data.Page404Data.PAGE_404_URL;
import static ru.yandex.autotests.mainmorda.data.Page404Data.REQUEST;
import static ru.yandex.autotests.mainmorda.data.Page404Data.SEARCH_BUTTON_TEXT_MATCHER;
import static ru.yandex.autotests.mainmorda.data.Page404Data.SEARCH_URL;
import static ru.yandex.autotests.mainmorda.data.Page404Data.YANDEX_LINK;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: eoff
 * Date: 07.02.13
 */
@Aqua.Test(title = "Страница 404")
@Features({"Main", "Plain", "Page 404"})
@Stories("View")
public class Page404Test {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private Page404 page404 = new Page404(driver);
    private LinksSteps userLink = new LinksSteps(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
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
    public void feedbackLink() {
        user.shouldSeeElement(page404.feedbackLink);
        user.shouldSeeElementWithText(page404.feedbackLink, getTranslation("home", "error404", "contact_us", CONFIG.getLang()));
        user.shouldSeeElementMatchingTo(page404.feedbackLink, hasAttribute(HREF, FEEDBACK_URL));
    }

    @Test
    public void noPageText() {
        user.shouldSeeElement(page404.noPageText);
        user.shouldSeeElementWithText(page404.noPageText, NO_PAGE_TEXT);
    }

    @Test
    public void companyRuLink() {
        userLink.shouldSeeLink(page404.companyRuLink, COMPANY_RU_LINK, ALL_SERVICES);
    }

    @Test
    public void companyComLink() {
        userLink.shouldSeeLink(page404.companyComLink, COMPANY_COM_LINK, ALL_SERVICES);
    }

    @Test
    public void yandexLink() {
        userLink.shouldSeeLink(page404.yandexLink, YANDEX_LINK, PAGE_404);
    }
}
