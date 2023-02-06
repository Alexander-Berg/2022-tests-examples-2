package ru.yandex.autotests.turkey.footer;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.turkey.pages.YandexComTrPage;
import ru.yandex.qatools.allure.annotations.Features;

import static ru.yandex.autotests.turkey.data.FooterData.COMPANY_LINK;
import static ru.yandex.autotests.turkey.data.FooterData.COPYRIGHT_TEXT_MATCHER;
import static ru.yandex.autotests.turkey.data.FooterData.DEFAULT_SEARCH_LINK;
import static ru.yandex.autotests.turkey.data.FooterData.FEEDBACK_LINK;
import static ru.yandex.autotests.turkey.data.FooterData.LEGAL_LINK;

/**
 * User: alex89
 * Date: 04.10.12
 */

@Aqua.Test(title = "Ссылки футера")
@Features("Footer")
public class FooterTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private YandexComTrPage yandexComTrPage = new YandexComTrPage(driver);

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL());
        user.setsRegion(CONFIG.getBaseDomain().getCapital());
        user.shouldSeeElement(yandexComTrPage.footerBlock);
    }

    @Test
    public void companyLink() {
        user.shouldSeeLink(yandexComTrPage.footerBlock.companyLink, COMPANY_LINK);
    }

    @Test
    public void feedbackLink() {
        user.shouldSeeLink(yandexComTrPage.footerBlock.feedbackLink, FEEDBACK_LINK);
    }

    @Test
    public void copyrightText() {
        user.shouldSeeElement(yandexComTrPage.footerBlock.copyrightText);
        user.shouldSeeElementWithText(yandexComTrPage.footerBlock.copyrightText,
                COPYRIGHT_TEXT_MATCHER);
    }

    @Test
    public void legalLink() {
        user.shouldSeeLink(yandexComTrPage.footerBlock.legalLink, LEGAL_LINK);
    }

    @Test
    public void defaultSearchLink() {
        user.shouldSeeLink(yandexComTrPage.footerBlock.defaultSearchLink, DEFAULT_SEARCH_LINK);
    }
}