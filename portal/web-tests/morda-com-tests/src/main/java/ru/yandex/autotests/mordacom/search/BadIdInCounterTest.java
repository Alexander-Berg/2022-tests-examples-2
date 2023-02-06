package ru.yandex.autotests.mordacom.search;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacom.Properties;
import ru.yandex.autotests.mordacom.pages.HomePage;
import ru.yandex.autotests.mordacom.steps.YandexUidSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static org.hamcrest.Matchers.equalTo;

/**
 * User: ivannik
 * Date: 10.07.13
 * Time: 18:41
 */
@Aqua.Test(title = "Отсутствие элементов с BADID")
@Features("Search")
@Stories("BADID")
@RunWith(Parameterized.class)
public class BadIdInCounterTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private YandexUidSteps userUid = new YandexUidSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> testData() {
        return ParametrizationConverter.convert(CONFIG.getMordaComLangs());
    }

    private final Language language;

    public BadIdInCounterTest(Language language) {
        this.language = language;
    }

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL());
        user.setsLanguageOnCom(language);
        userUid.setsUIDWithCounters();
        user.refreshPage();
    }

    @Test
    public void badIdNotExists() {
        user.shouldSeeListWithSize(homePage.elementsWithBadId, equalTo(0));
    }
}
