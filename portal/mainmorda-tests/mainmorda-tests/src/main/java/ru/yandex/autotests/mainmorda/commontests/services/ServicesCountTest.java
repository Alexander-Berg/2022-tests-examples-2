package ru.yandex.autotests.mainmorda.commontests.services;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.blocks.ServicesBlock;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.List;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.hasItems;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.mordaexportslib.data.ServicesData.getNoSignServices;
import static ru.yandex.autotests.mordaexportslib.data.ServicesData.getPinnedSignServices;
import static ru.yandex.autotests.mordaexportslib.data.ServicesData.getRotatingSignServices;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: eoff
 * Date: 12.12.12
 */
@Aqua.Test(title = "Количество сервисов (вид по-умолчанию)")
@Features({"Main", "Common", "Services Block"})
@Stories("Count")
public class ServicesCountTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void setUp() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        user.shouldSeeElement(mainPage.servicesBlock);
    }

    @Test
    public void defaultServicesSignList() {
        List<ServicesV122Entry> availableSignEntries = new ArrayList<>();
        availableSignEntries.addAll(getPinnedSignServices(CONFIG.getBaseDomain().getCapital(), "v12"));
        availableSignEntries.addAll(getRotatingSignServices(CONFIG.getBaseDomain().getCapital(), "v12"));

        List<String> availableNames = new ArrayList<>();
        List<String> actualNames = new ArrayList<>();

        for (ServicesV122Entry e : availableSignEntries) {
            availableNames.add(getTranslation("home", "services", "services." + e.getId() + ".title", CONFIG.getLang()));
        }
        for (ServicesBlock.HtmlLinkWithComment e : mainPage.servicesBlock.serviceLinksWithComments) {
            actualNames.add(e.serviceLink.getText());
        }

        assertThat(availableNames, hasItems(actualNames.toArray(new String[actualNames.size()])));
    }

    @Test
    public void defaultServicesSignNumber() {
        int available = getPinnedSignServices(CONFIG.getBaseDomain().getCapital(), "v12").size()
                + getRotatingSignServices(CONFIG.getBaseDomain().getCapital(), "v12").size();
        user.shouldSeeListWithSize(mainPage.servicesBlock.serviceLinksWithComments,
                equalTo(Math.min(7, available)));
    }

    @Test
    public void defaultServicesNoSignNumber() {
        user.shouldSeeListWithSize(mainPage.servicesBlock.serviceLinksWithoutComments,
                equalTo(getNoSignServices(CONFIG.getBaseDomain().getCapital(), "v12").size()));
    }
}
