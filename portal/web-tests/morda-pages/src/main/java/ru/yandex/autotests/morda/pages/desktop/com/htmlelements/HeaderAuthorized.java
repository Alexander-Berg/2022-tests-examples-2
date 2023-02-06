package ru.yandex.autotests.morda.pages.desktop.com.htmlelements;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.com.DesktopComMorda;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.IconLink;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.CLASS;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: asamar
 * Date: 30.09.2015.
 */
@Name("Авторизованный хедер")
@FindBy(xpath = "//div[contains(@class, 'b-line__bar-right')]")
public class HeaderAuthorized extends HtmlElement implements Validateable<DesktopComMorda> {

    @Name("Переключалка языка")
    @FindBy(xpath = ".//span[contains(@class, 'link dropdown-menu__switcher')]")
    public HtmlElement langSwitcher;

    @Name("Имя юзера")
    @FindBy(xpath = ".//a[contains(@class, 'link user')]")
    public HtmlElement userNameLink;

    @Name("Иконка с письмами")
    @FindBy(xpath = ".//a[contains(@class, 'user__count')]")
    public IconLink mailsLink;

    @Name("Ссылка на 'exit'")
    @FindBy(xpath = ".//a[contains(@class, 'user__exit')]")
    public HtmlElement exitLink;


    @Override
    public HierarchicalErrorCollector validate(Validator<? extends DesktopComMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateLangSwitcher(langSwitcher, validator),
                        validateUserName(userNameLink, validator),
                        validateMails(mailsLink, validator),
                        validateExitLink(exitLink, validator)
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateLangSwitcher(HtmlElement langSwitcher,
                                                                  Validator<? extends DesktopComMorda> validator) {

        return collector()
                .check(shouldSeeElement(langSwitcher))
                .check(shouldSeeElementMatchingTo(langSwitcher, hasText(validator.getCleanvars().getLanguage())));
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateUserName(HtmlElement userNameLink,
                                                              Validator<? extends DesktopComMorda> validator) {

        return collector()
                .check(shouldSeeElement(userNameLink))
                .check(shouldSeeElementMatchingTo(userNameLink,
                                hasText(validator.getCleanvars().getAuthInfo().getDisplayName()))

                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateMails(IconLink mailsLink,
                                                           Validator<? extends DesktopComMorda> validator) {

        return collector()
                .check(shouldSeeElement(mailsLink))
                .check(
                        shouldSeeElementMatchingTo(mailsLink,
                                hasText(String.valueOf(validator.getCleanvars().getMail().getCount()))),
                        shouldSeeElementMatchingTo(mailsLink.i,
                                hasAttribute(CLASS, equalTo("b-ico b-ico-mail")))
                );
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateExitLink(HtmlElement exitLink,
                                                              Validator<? extends DesktopComMorda> validator) {

        return collector()
                .check(shouldSeeElement(exitLink))
                .check(shouldSeeElementMatchingTo(exitLink,
                        hasText(getTranslation("home","spok_yes","head.logout", validator.getMorda().getLanguage()))));
    }
}
