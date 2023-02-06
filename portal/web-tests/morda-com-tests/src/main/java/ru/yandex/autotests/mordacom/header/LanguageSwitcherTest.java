package ru.yandex.autotests.mordacom.header;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacom.Properties;
import ru.yandex.autotests.mordacom.data.HeaderData;
import ru.yandex.autotests.mordacom.pages.HomePage;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.language.LanguageManager;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.LANGUAGE_NAME;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
@Aqua.Test(title = "Переключалка языка")
@Features("Header")
@Stories("Language Switcher")
@RunWith(Parameterized.class)
public class LanguageSwitcherTest {
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

    public LanguageSwitcherTest(Language language) {
        this.language = language;
    }

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL());
        user.setsLanguageOnCom(language);
        user.shouldSeeElement(homePage.headerBlock);
    }

    @Test
    public void switcherAppearance() {
        user.shouldSeeElement(homePage.headerBlock.languageSwitcher);
        user.shouldSeeElementWithText(homePage.headerBlock.languageSwitcher, language.getValue().toUpperCase());

        user.clicksOn(homePage.headerBlock.languageSwitcher);
        user.shouldSeeElement(homePage.headerBlock.languageSwitcherPopup);

        user.shouldSeeElement(homePage.headerBlock.languageSwitcherPopup.currentLanguage);
        user.shouldSeeElementWithText(homePage.headerBlock.languageSwitcherPopup.currentLanguage,
                getTranslation(LANGUAGE_NAME, language));

        user.shouldSeeElement(homePage.headerBlock.languageSwitcherPopup.availableLanguage);
        user.shouldSeeElementWithText(homePage.headerBlock.languageSwitcherPopup.availableLanguage,
                getTranslation(LANGUAGE_NAME, HeaderData.AVALIABLE_LANG.get(language)));
    }

    @Test
    public void languageSwitch() {
        user.shouldSeeElement(homePage.headerBlock.languageSwitcher);
        user.clicksOn(homePage.headerBlock.languageSwitcher);
        user.shouldSeeElement(homePage.headerBlock.languageSwitcherPopup);
        user.shouldSeeElement(homePage.headerBlock.languageSwitcherPopup.availableLanguage);
        user.clicksOn(homePage.headerBlock.languageSwitcherPopup.availableLanguage);

        user.shouldSeePage(CONFIG.getBaseURL());
        user.shouldNotSeeElement(homePage.headerBlock.languageSwitcherPopup);
        user.shouldSeeElement(homePage.headerBlock.languageSwitcher);
        user.shouldSeeElementWithText(homePage.headerBlock.languageSwitcher,
                HeaderData.AVALIABLE_LANG.get(language).getValue().toUpperCase());
    }

}
