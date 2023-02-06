package ru.yandex.autotests.morda.pages.desktop.com.htmlelements;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.com.DesktopComMorda;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.IconLink;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.MAIL_LOGIN;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: asamar
 * Date: 30.09.2015.
 */
@Name("Неавторизованный хедер")
@FindBy(xpath = "//div[contains(@class, 'b-line__bar-right')]")
public class HeaderUnauthorized extends HtmlElement implements Validateable<DesktopComMorda> {

    @Name("Ссылка 'Log in'")
    @FindBy(xpath = ".//a[contains(@class, 'link_black_novisit link b-inline')]")
    public IconLink logInLink;

    @Name("Переключалка языка")
    @FindBy(xpath = ".//span[contains(@class, 'link dropdown-menu__switcher')]")
    public HtmlElement langSwitcher;

    @Override
    public HierarchicalErrorCollector validate(Validator<? extends DesktopComMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateLogIn(logInLink, validator),
                        validateLangSwitcher(langSwitcher, validator));
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateLogIn(IconLink logInLink,
                                                           Validator<? extends DesktopComMorda> validator) {
        return collector()
                .check(shouldSeeElement(logInLink))
                .check(
                        shouldSeeElementMatchingTo(logInLink, allOfDetailed(
                                hasText(equalTo(getTranslation(MAIL_LOGIN, validator.getMorda().getLanguage()))),
                                hasAttribute(HREF, equalTo(validator.getCleanvars().getMail().getHref())))),
                        shouldSeeElementMatchingTo(logInLink.i,
                                hasAttribute(HtmlAttribute.CLASS, equalTo("b-ico b-ico-mail")))

                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateLangSwitcher(HtmlElement langSwitcher,
                                                                  Validator<? extends DesktopComMorda> validator) {

        return collector()
                .check(shouldSeeElement(langSwitcher))
                .check(shouldSeeElementMatchingTo(langSwitcher, hasText(validator.getCleanvars().getLanguage())));
    }
}
