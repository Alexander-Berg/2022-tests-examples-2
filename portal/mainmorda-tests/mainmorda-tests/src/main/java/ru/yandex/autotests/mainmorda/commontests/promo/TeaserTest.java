package ru.yandex.autotests.mainmorda.commontests.promo;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.steps.ModeSteps;
import ru.yandex.autotests.mainmorda.steps.PromoSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.qatools.allure.annotations.Features;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.not;
import static org.hamcrest.text.IsEmptyString.isEmptyOrNullString;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;

/**
 * User: alex89
 * Date: 07.12.12
 */
@Aqua.Test(title = "Ссылка, описание")
@Features({"Main", "Common", "Teaser"})
public class TeaserTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private ModeSteps userMode = new ModeSteps(driver);
    private PromoSteps userPromo = new PromoSteps(driver);
    private MainPage mainPage = new MainPage(driver);

    @Before
    public void initLanguage() {
        user.initTest(CONFIG.getBaseURL(), CONFIG.getBaseDomain().getCapital(), CONFIG.getLang());
        userMode.setMode(CONFIG.getMode(), mordaAllureBaseRule);
        user.shouldSeeElement(mainPage.teaserBlock);
    }

    @Test
    public void promoAndImageSource() {
        user.shouldSeeElement(mainPage.teaserBlock.promoLink);
        user.shouldSeeElement(mainPage.teaserBlock.promoImageLink);
        userPromo.shouldSeeThatPromoLinkAndImageHaveSameYabsHref();
    }

    @Test
    public void promoHasDescription() {
        user.shouldSeeElement(mainPage.teaserBlock.promoLink);
        user.shouldSeeElement(mainPage.teaserBlock.promoDescription);
        user.shouldSeeElementWithText(mainPage.teaserBlock.promoDescription, not(equalTo("")));
    }

    @Test
    public void promoImageAlt() {
        user.shouldSeeElement(mainPage.teaserBlock.promoImage);
        user.shouldSeeElementMatchingTo(mainPage.teaserBlock.promoImage,
                hasAttribute(HtmlAttribute.ALT, not(isEmptyOrNullString())));
    }
}
