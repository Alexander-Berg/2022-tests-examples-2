package ru.yandex.autotests.mainmorda.commontests.footer;

import org.junit.Assume;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.LinksSteps;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.qatools.allure.annotations.Features;

import static ru.yandex.autotests.mainmorda.blocks.PageBlock.FOOTER;
import static ru.yandex.autotests.mainmorda.data.FooterData.COPYRIGHT_TEXT;
import static ru.yandex.autotests.mainmorda.data.FooterData.DESIGN_LOGOFF_TEXT;
import static ru.yandex.autotests.mainmorda.data.FooterData.LINK_ABOUT;
import static ru.yandex.autotests.mainmorda.data.FooterData.LINK_ADV;
import static ru.yandex.autotests.mainmorda.data.FooterData.LINK_ARTLEBEDEV;
import static ru.yandex.autotests.mainmorda.data.FooterData.LINK_BLOG;
import static ru.yandex.autotests.mainmorda.data.FooterData.LINK_COMPANY;
import static ru.yandex.autotests.mainmorda.data.FooterData.LINK_DIRECT;
import static ru.yandex.autotests.mainmorda.data.FooterData.LINK_DIRECT_COMMENT;
import static ru.yandex.autotests.mainmorda.data.FooterData.LINK_FEEDBACK;
import static ru.yandex.autotests.mainmorda.data.FooterData.LINK_HELP;
import static ru.yandex.autotests.mainmorda.data.FooterData.LINK_METRIKA;
import static ru.yandex.autotests.mainmorda.data.FooterData.LINK_VACANCIES;
import static ru.yandex.autotests.mainmorda.data.FooterData.LINK_YANDEX_DEFAULT;

/**
 * User: leonsabr
 * Date: 23.03.12
 */
@Aqua.Test(title = "Ссылки Футера")
@Features({"Main", "Common", "Footer"})
public class FooterTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private MainPage mainPage = new MainPage(driver);
    private LinksSteps userLink = new LinksSteps(driver);

    @Before
    public void before() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
    }

    @Test
    public void aboutLink() {
        userLink.shouldSeeLink(mainPage.footerBlock.aboutLink, LINK_ABOUT, FOOTER);
    }

    @Test
    public void companyLink() {
        userLink.shouldSeeLink(mainPage.footerBlock.companyLink, LINK_COMPANY, FOOTER);
    }

    @Test
    public void copyrightText() {
        user.shouldSeeElementWithText(mainPage.footerBlock.copyrightText,
                COPYRIGHT_TEXT);
    }

    @Test
    public void artLebedevLink() {
        userLink.shouldSeeLink(mainPage.footerBlock.artLebedevStudioLink,
                LINK_ARTLEBEDEV, FOOTER);
    }

    @Test
    public void designText() {
        user.shouldSeeElementWithText(mainPage.footerBlock.designTextAndLink,
                DESIGN_LOGOFF_TEXT);
        user.logsOut();
        user.shouldSeeElementWithText(mainPage.footerBlock.designTextAndLink,
                DESIGN_LOGOFF_TEXT);
    }

    @Test
    public void directLink() {
        userLink.shouldSeeLink(mainPage.footerBlock.directLink, LINK_DIRECT, FOOTER);
    }

    @Test
    public void directCommentLink() {
        userLink.shouldSeeLink(mainPage.footerBlock.directCommentLink, LINK_DIRECT_COMMENT, FOOTER);
    }

    @Test
    public void advLink() {
        userLink.shouldSeeLink(mainPage.footerBlock.advLink,
                LINK_ADV, FOOTER);
    }

    @Test
    public void vacanciesLink() {
        userLink.shouldSeeLink(mainPage.footerBlock.vacanciesLink,
                LINK_VACANCIES, FOOTER);
    }

    @Test
    public void feedbackLink() {
        userLink.shouldSeeLink(mainPage.footerBlock.feedbackLink,
                LINK_FEEDBACK, FOOTER);
    }

    @Test
    public void yandexByDefaultLink() {
        Assume.assumeTrue("Cсылка 'Яндекс по умолчанию' есть только на .ru", CONFIG.getBaseDomain().equals(Domain.RU));
        userLink.shouldSeeLink(mainPage.footerBlock.yandexDefaultLink,
                LINK_YANDEX_DEFAULT, FOOTER);
    }

    @Test
    public void helpLink() {
        userLink.shouldSeeLink(mainPage.footerBlock.helpLink,
                LINK_HELP, FOOTER);
    }

    @Test
    public void metrikaLink() {
        userLink.shouldSeeLink(mainPage.footerBlock.metrikaLink,
                LINK_METRIKA, FOOTER);
    }

    @Test
    public void blogLink() {
        userLink.shouldSeeLink(mainPage.footerBlock.blogLink, LINK_BLOG, FOOTER);
    }
}
