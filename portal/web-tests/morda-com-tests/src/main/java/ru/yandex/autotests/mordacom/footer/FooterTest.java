package ru.yandex.autotests.mordacom.footer;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacom.Properties;
import ru.yandex.autotests.mordacom.pages.HomePage;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.Collection;

import static ru.yandex.autotests.mordacom.data.FooterData.COPYRIGHT_TEXT_MATCHER;
import static ru.yandex.autotests.mordacom.data.FooterData.getAboutLink;
import static ru.yandex.autotests.mordacom.data.FooterData.getLinkCopyrightNotice;
import static ru.yandex.autotests.mordacom.data.FooterData.getLinkPrivacyPolicy;
import static ru.yandex.autotests.mordacom.data.FooterData.getLinkTermsOfService;
import static ru.yandex.autotests.mordacom.data.FooterData.getTechnologiesLink;

/**
 * User: leonsabr
 * Date: 18.08.2010
 * Проверка текста копирайта и ссылкок
 */
@Aqua.Test(title = "Проверка футера")
@Features("Footer")
@RunWith(Parameterized.class)
public class FooterTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> testData() {
        return ParametrizationConverter.convert(CONFIG.getMordaComLangs());
    }

    private final Language language;

    public FooterTest(Language language) {
        this.language = language;
    }

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL());
        user.setsLanguageOnCom(language);
    }

    @Test
    public void technologiesLink() {
        user.shouldSeeLink(homePage.footerBlock.technologiesLink, getTechnologiesLink(language));
    }

    @Test
    public void aboutLink() {
        user.shouldSeeLink(homePage.footerBlock.aboutLink, getAboutLink(language));
    }

    @Test
    public void termsOfServiceLink() {
        user.shouldSeeLink(homePage.footerBlock.termsOfServiceLink, getLinkTermsOfService(language));
    }

    @Test
    public void privacyLink() {
        user.shouldSeeLink(homePage.footerBlock.privacyLink, getLinkPrivacyPolicy(language));
    }

    @Test
    public void copyrightLink() {
        user.shouldSeeLink(homePage.footerBlock.copyrightLink, getLinkCopyrightNotice(language));
    }

    @Test
    public void copyrightText() {
        user.shouldSeeElement(homePage.footerBlock.copyrightText);
        user.shouldSeeElementWithText(homePage.footerBlock.copyrightText,
                COPYRIGHT_TEXT_MATCHER);
    }
}
