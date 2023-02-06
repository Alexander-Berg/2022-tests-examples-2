package ru.yandex.autotests.turkey.football;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.turkey.pages.YandexComTrPage;
import ru.yandex.autotests.turkey.steps.FootballSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.autotests.utils.morda.cookie.Cookie;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.Collection;

import static ru.yandex.autotests.turkey.data.FootballData.CANCEL_LINK;
import static ru.yandex.autotests.turkey.data.FootballData.FootballClub;
import static ru.yandex.autotests.turkey.data.FootballData.FootballClub.getAllClubs;
import static ru.yandex.autotests.turkey.data.FootballData.QUESTION_TEXT;
import static ru.yandex.autotests.turkey.data.FootballData.getAcceptLink;
import static ru.yandex.autotests.turkey.data.FootballData.getResetLink;

/**
 * User: Poluektov Evgeniy <poluektov@yandex-team.ru>
 * on: 28.11.2014.
 */

@Aqua.Test(title = "Футбольные морды")
@Features("Football")
@RunWith(Parameterized.class)
public class SaveFootballPageTest {
    private static final Properties CONFIG = new Properties();
    private FootballClub club;

    public SaveFootballPageTest(FootballClub curClub) {
        this.club = curClub;
    }

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private FootballSteps userFootball = new FootballSteps(driver);
    private YandexComTrPage yandexComTrPage = new YandexComTrPage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        return ParametrizationConverter.convert(getAllClubs());
    }

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL());
        user.addCookie(driver, Cookie.MDA, "0");
    }

    @Test
    public void hasCorrectPopupContent() {
        user.opensPage(club.getFootballClubUrl());
        user.shouldSeeElement(yandexComTrPage.saveFootballStyleBlock);
        user.shouldSeeElementWithText(yandexComTrPage.saveFootballStyleBlock.popUpText,
                QUESTION_TEXT);

        user.shouldSeeElementWithText(yandexComTrPage.saveFootballStyleBlock.popUpCancelButton, CANCEL_LINK.text);
        user.shouldSeeElementMatchingTo(yandexComTrPage.saveFootballStyleBlock.popUpCancelButton,
                CANCEL_LINK.attributes);

        LinkInfo acceptLink = getAcceptLink(driver, club);
        user.shouldSeeElementWithText(yandexComTrPage.saveFootballStyleBlock.popUpSaveButton, acceptLink.text);
        user.shouldSeeElementMatchingTo(yandexComTrPage.saveFootballStyleBlock.popUpSaveButton, acceptLink.attributes);

    }

    @Test
    public void saveFootballThemeOpenMainPageAndReset() {
        user.opensPage(club.getFootballClubUrl());
        user.shouldSeeElement(yandexComTrPage.saveFootballStyleBlock);
        user.shouldSeeElement(yandexComTrPage.saveFootballStyleBlock.popUpSaveButton);
        user.clicksOn(yandexComTrPage.saveFootballStyleBlock.popUpSaveButton);
        try {
            Thread.sleep(3000);
        } catch (InterruptedException e) {
            throw new RuntimeException(e.getMessage());
        }
        user.shouldNotSeeElement(yandexComTrPage.saveFootballStyleBlock);
        user.opensPage(CONFIG.getBaseURL());
        userFootball.shouldSeeFootballStyle(club);

        LinkInfo resetLink = getResetLink(driver);
        user.shouldSeeElement(yandexComTrPage.footerBlock.setDefaultLink);
        user.shouldSeeElementWithText(yandexComTrPage.footerBlock.setDefaultLink, resetLink.text);
        user.shouldSeeElementMatchingTo(yandexComTrPage.footerBlock.setDefaultLink, resetLink.attributes);
        user.clicksOn(yandexComTrPage.footerBlock.setDefaultLink);
        try {
            Thread.sleep(3000);
        } catch (InterruptedException e) {
            throw new RuntimeException(e.getMessage());
        }
        user.shouldNotSeeElement(yandexComTrPage.footballStyle);
        user.shouldNotSeeElement(yandexComTrPage.footerBlock.setDefaultLink);
    }

    @Test
    public void doNotSaveFootballThemeAndOpenMainPage() {
        user.opensPage(club.getFootballClubUrl());
        user.shouldSeeElement(yandexComTrPage.saveFootballStyleBlock);
        user.shouldSeeElement(yandexComTrPage.saveFootballStyleBlock.popUpCancelButton);
        user.clicksOn(yandexComTrPage.saveFootballStyleBlock.popUpCancelButton);
        user.shouldNotSeeElement(yandexComTrPage.saveFootballStyleBlock);
        user.opensPage(CONFIG.getBaseURL());
        user.shouldNotSeeElement(yandexComTrPage.footballStyle);
        user.shouldNotSeeElement(yandexComTrPage.footerBlock.setDefaultLink);
    }

    @Test
    public void refreshFootballPage() {
        user.opensPage(club.getFootballClubUrl());
        user.shouldSeeElement(yandexComTrPage.saveFootballStyleBlock);
        user.refreshPage();
        user.shouldNotSeeElement(yandexComTrPage.saveFootballStyleBlock);
    }

    @Test
    public void footballUserOpensOwnFootballPage() {
        userFootball.setFootballStyle(club);
        user.opensPage(club.getFootballClubUrl());
        user.shouldNotSeeElement(yandexComTrPage.saveFootballStyleBlock);
    }

    @Test
    public void footballUserOpensMainPage() {
        userFootball.setFootballStyle(club);
        user.opensPage(CONFIG.getBaseURL());
        user.shouldSeeElement(yandexComTrPage.footballStyle);
        user.shouldNotSeeElement(yandexComTrPage.footerBlock.setDefaultLink);
    }
}
