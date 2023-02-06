package ru.yandex.autotests.mainmorda.steps;

import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.blocks.PageBlock;
import ru.yandex.autotests.mainmorda.utils.LinkHrefInfo;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static ru.yandex.autotests.mainmorda.matchers.ElementHrefMatcher.hasHref;

/**
 * User: alex89
 * Date: 30.10.12
 */
public class LinksSteps {
    private static final Properties CONFIG = new Properties();

    private WebDriver driver;
    private CommonMordaSteps userSteps;

    public LinksSteps(WebDriver driver) {
        this.driver = driver;
        this.userSteps = new CommonMordaSteps(driver);
    }

    @Step("Should see link: {1}")
    public void shouldSeeLink(HtmlElement link, LinkInfo info, PageBlock block) {
        userSteps.shouldSeeElement(link);
        userSteps.shouldSeeElementWithText(link, info.text);
        userSteps.shouldSeeElementMatchingTo(link, info.attributes);
//        if (CONFIG.getMordaEnv().isProd() && link.getAttribute(HREF.getValue()) != null) {
//            addLink(
//                    mordaLink(link.getAttribute(HREF.getValue()))
//                            .cond(new MordaConditions()
//                                    .withGid(CONFIG.getBaseDomain().getCapital().getRegionId())
//                                    .withBlock(block.name())
//                                    .withLang(CONFIG.getLang().getValue())
//                                    .withAuth(isLogged().matches(driver))
//                            )
//            );
//        }
    }

    @Step("Should see link: {1}")
    public void shouldSeeHref(HtmlElement link, LinkHrefInfo info) {
        userSteps.shouldSeeElement(link);
        userSteps.shouldSeeElementWithText(link, info.text);
        userSteps.shouldSeeElementMatchingTo(link, hasHref(info.href, (JavascriptExecutor) driver));
    }
}
