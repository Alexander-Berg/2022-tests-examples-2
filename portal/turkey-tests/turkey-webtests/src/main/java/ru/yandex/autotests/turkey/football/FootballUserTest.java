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
import ru.yandex.autotests.turkey.data.FootballData;
import ru.yandex.autotests.turkey.pages.YandexComTrPage;
import ru.yandex.autotests.turkey.steps.FootballSteps;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.turkey.data.FootballData.CANCEL_LINK;
import static ru.yandex.autotests.turkey.data.FootballData.FootballClub;
import static ru.yandex.autotests.turkey.data.FootballData.FootballClub.getAllClubs;
import static ru.yandex.autotests.turkey.data.FootballData.FootballClub.getAllOtherClubs;
import static ru.yandex.autotests.turkey.data.FootballData.QUESTION_TEXT;
import static ru.yandex.autotests.turkey.data.FootballData.getAcceptLink;

/**
 * User: Poluektov Evgeniy <poluektov@yandex-team.ru>
 * on: 03.12.2014.
 */
@Aqua.Test(title = "Футбольные морды: футбольный браузер на странице чужого клуба")
@Features("Football")
@RunWith(Parameterized.class)
public class FootballUserTest {
    private static final Properties CONFIG = new Properties();
    private FootballClub club;
    private FootballClub anotherClub;

    public FootballUserTest(FootballClub club, FootballClub anotherClub) {
        this.club = club;
        this.anotherClub = anotherClub;
    }

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private FootballSteps userFootball = new FootballSteps(driver);
    private YandexComTrPage yandexComTrPage = new YandexComTrPage(driver);

    @Parameterized.Parameters(name = "{0}, {1}")
    public static Collection<Object[]> data() {
        List<FootballData.FootballClub> all = getAllClubs();
        List<Object[]> inputData = new ArrayList<>();
        for (FootballClub footballClub : all) {
            List<FootballData.FootballClub> other = getAllOtherClubs(footballClub);
            for (FootballClub otherClub : other) {
                inputData.add(new Object[]{footballClub, otherClub});
            }
        }
        return inputData;
    }

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL());
        userFootball.setFootballStyle(club);
        user.opensPage(anotherClub.getFootballClubUrl());
    }

    @Test
    public void footballUserHasCorrectPopup() {
        user.shouldSeeElement(yandexComTrPage.saveFootballStyleBlock);
        user.shouldSeeElementWithText(yandexComTrPage.saveFootballStyleBlock.popUpText, QUESTION_TEXT);

        user.shouldSeeElementWithText(yandexComTrPage.saveFootballStyleBlock.popUpCancelButton, CANCEL_LINK.text);
        user.shouldSeeElementMatchingTo(yandexComTrPage.saveFootballStyleBlock.popUpCancelButton,
                CANCEL_LINK.attributes);

        LinkInfo acceptLink = getAcceptLink(driver, anotherClub);
        user.shouldSeeElementWithText(yandexComTrPage.saveFootballStyleBlock.popUpSaveButton, acceptLink.text);
        user.shouldSeeElementMatchingTo(yandexComTrPage.saveFootballStyleBlock.popUpSaveButton, acceptLink.attributes);
    }

    @Test
    public void footballUserHasPopupAndRefreshesPage() {
        user.shouldSeeElement(yandexComTrPage.saveFootballStyleBlock);
        user.refreshPage();
        user.shouldNotSeeElement(yandexComTrPage.saveFootballStyleBlock);
    }

    @Test
    public void footballUserSavesAnotherClub() {
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
        userFootball.shouldSeeFootballStyle(anotherClub);
    }

    @Test
    public void setDefaultThemeTest() {
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
        user.shouldSeeElement(yandexComTrPage.footerBlock.setDefaultLink);
        user.clicksOn(yandexComTrPage.footerBlock.setDefaultLink);
        userFootball.shouldSeeFootballStyle(club);
    }
}
