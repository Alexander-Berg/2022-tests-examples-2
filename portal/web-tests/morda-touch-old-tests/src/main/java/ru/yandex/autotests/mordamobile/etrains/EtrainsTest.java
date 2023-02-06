package ru.yandex.autotests.mordamobile.etrains;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.pages.HomePage;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.Collection;

import static org.hamcrest.Matchers.greaterThan;
import static ru.yandex.autotests.mordamobile.data.EtrainsData.ETRAINS_REGIONS;
import static ru.yandex.autotests.mordamobile.data.EtrainsData.getEtrainsTitleLink;
import static ru.yandex.autotests.mordamobile.data.EtrainsData.getEtrainsRaspLink;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;

/**
 * User: ivannik
 * Date: 10.09.2014
 */
@Aqua.Test(title = "Блок электричек")
@Features("Etrains")
@RunWith(Parameterized.class)
public class EtrainsTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private HomePage homePage = new HomePage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        return convert(ETRAINS_REGIONS);
    }

    private Region region;

    public EtrainsTest(Region region) {
        this.region = region;
    }

    @Before
    public void setUp() throws Exception {
        user.initTest(CONFIG.getBaseURL(), region, CONFIG.getLang());
        user.shouldSeeElement(homePage.etrainsBlock);
    }

    @Test
    public void etrainsTitle() {
        user.shouldSeeElement(homePage.etrainsBlock.title);
        user.shouldSeeLink(homePage.etrainsBlock.title, getEtrainsTitleLink(region));
    }

    @Test
    public void etrainsDirection() {
        user.shouldSeeElement(homePage.etrainsBlock.directionBlock1);
        user.shouldNotSeeElement(homePage.etrainsBlock.directionBlock2);

        user.shouldSeeElement(homePage.etrainsBlock.directionBlock1.directionLink);
        user.clicksOn(homePage.etrainsBlock.directionBlock1.directionLink);

        user.shouldSeeElement(homePage.etrainsBlock.directionBlock2);
        user.shouldNotSeeElement(homePage.etrainsBlock.directionBlock1);
    }

    @Test
    public void etrainsTimes() {
        user.shouldSeeElement(homePage.etrainsBlock.directionBlock1);
        user.shouldSeeListWithSize(homePage.etrainsBlock.directionBlock1.timeLinks, greaterThan(0));
        for (HtmlElement element : homePage.etrainsBlock.directionBlock1.timeLinks) {
            user.shouldSeeElement(element);
        }

        user.shouldSeeElement(homePage.etrainsBlock.directionBlock1.directionLink);
        user.clicksOn(homePage.etrainsBlock.directionBlock1.directionLink);

        user.shouldSeeElement(homePage.etrainsBlock.directionBlock2);
        user.shouldSeeListWithSize(homePage.etrainsBlock.directionBlock2.timeLinks, greaterThan(0));
        for (HtmlElement element : homePage.etrainsBlock.directionBlock2.timeLinks) {
            user.shouldSeeElement(element);
        }
    }

    @Test
    public void etrainsHint() {
        user.shouldSeeElement(homePage.etrainsBlock.directionBlock1);
        user.shouldSeeListWithSize(homePage.etrainsBlock.directionBlock1.timeLinks, greaterThan(0));
        user.clicksOn(homePage.etrainsBlock.directionBlock1.timeLinks.get(0));
        user.shouldSeeElement(homePage.etrainsBlock.directionBlock1.hint);
        user.shouldSeeLinkLight(homePage.etrainsBlock.directionBlock1.hint.raspLink, getEtrainsRaspLink(region));

        user.shouldSeeElement(homePage.etrainsBlock.directionBlock1.directionLink);
        user.clicksOn(homePage.etrainsBlock.directionBlock1.directionLink);


        user.shouldSeeElement(homePage.etrainsBlock.directionBlock2);
        user.shouldSeeListWithSize(homePage.etrainsBlock.directionBlock2.timeLinks, greaterThan(0));
        user.clicksOn(homePage.etrainsBlock.directionBlock2.timeLinks.get(0));
        user.shouldSeeElement(homePage.etrainsBlock.directionBlock2.hint);
        user.shouldSeeLink(homePage.etrainsBlock.directionBlock2.hint.raspLink, getEtrainsRaspLink(region));
    }
}
