package ru.yandex.autotests.morda.pages.desktop.yaru.htmlelements;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.yaru.DesktopYaruMorda;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.utils.morda.language.Dictionary;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.Matchers.equalTo;
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
 * Date: 23/04/15
 */
@Name("Неавторизованный хедер")
@FindBy(xpath = "//div[contains(@class, 'personal')]")
public class HeaderUnauthorized extends HtmlElement implements Validateable<DesktopYaruMorda> {

    @Name("Ссылка \"Войти в почту\"")
    @FindBy(xpath = ".//a[contains(@class, 'link_logout')]")
    private HtmlElement loginLink;

    @Override
    public HierarchicalErrorCollector validate(Validator<? extends DesktopYaruMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(

                        validateLoginLink(validator)
                );
    }

    @Step("Check login link")
    public HierarchicalErrorCollector validateLoginLink(Validator<? extends DesktopYaruMorda> validator) {
        return collector()
                .check(shouldSeeElement(loginLink))
                .check(shouldSeeElementMatchingTo(loginLink, allOfDetailed(
                        hasText(equalTo(getTranslation(Dictionary.Home.Head.LOGIN, validator.getMorda().getLanguage()))),
                        hasAttribute(HREF, equalTo("https://mail.yandex.ru/"))
                )));
    }

}
