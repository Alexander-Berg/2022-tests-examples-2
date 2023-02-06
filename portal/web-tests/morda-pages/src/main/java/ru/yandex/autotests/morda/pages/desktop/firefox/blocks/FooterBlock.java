package ru.yandex.autotests.morda.pages.desktop.firefox.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.firefox.DesktopFirefoxMorda;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.utils.morda.language.Dictionary;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 22/04/15
 */
@Name("Футер")
@FindBy(xpath = "//div[contains(@class, 'mfooter')]")
public class FooterBlock extends HtmlElement implements Validateable<DesktopFirefoxMorda> {

    @Name("Ссылка \"О Mozilla\"")
    @FindBy(xpath = ".//a[1]")
    private HtmlElement mozillaLink;

    @Name("Ссылка \"© Яндекс\"")
    @FindBy(xpath = ".//a[2]")
    private HtmlElement yandexLink;

    @Override
    @Step("Check footer")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopFirefoxMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateMozillaLink(validator),
                        validateYandexLink(validator)
                );
    }

    @Step("Check mozilla link")
    public HierarchicalErrorCollector validateMozillaLink(Validator<? extends DesktopFirefoxMorda> validator) {
        return collector()
                .check(shouldSeeElement(mozillaLink))
                .check(shouldSeeElementMatchingTo(mozillaLink, allOfDetailed(
                        hasText(getTranslation(Dictionary.Home.Foot.ABOUT_MOZILLA, validator.getMorda().getLanguage())),
                        hasAttribute(HREF, equalTo(validator.getMorda().getScheme() + "://www.mozilla.com/about/"))
                )));
    }

    @Step("Check yandex link")
    public HierarchicalErrorCollector validateYandexLink(Validator<? extends DesktopFirefoxMorda> validator) {
        return collector()
                .check(shouldSeeElement(yandexLink))
                .check(shouldSeeElementMatchingTo(yandexLink, allOfDetailed(
                        hasText("© " + getTranslation(Dictionary.Home.Main.YANDEX, validator.getMorda().getLanguage())),
//                        hasAttribute(HREF, startsWith(validator.getMorda().getScheme() + "://www.yandex."))
                        hasAttribute(HREF, startsWith(validator.getCleanvars().getWWW()))
                )));
    }


}
