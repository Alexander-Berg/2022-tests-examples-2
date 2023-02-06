package ru.yandex.autotests.morda.pages.touch.comtr.htmlelements.header;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithLoginLink;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithUsername;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.comtr.TouchComTrMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.morda.steps.CheckSteps;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.HEAD_ENTER;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 31/03/15
 */
@Name("Блок с именем пользователя")
@FindBy(xpath = "//div[contains(@class, 'mheader__user')]")
public class UserBlock extends HtmlElement implements BlockWithUsername, BlockWithLoginLink,
        Validateable<TouchComTrMorda> {

    private static final CheckSteps CHECK_STEPS = new CheckSteps();

    @Name("Ссылка \"Войти\"")
    @FindBy(xpath = ".//div[contains(@class, 'user-login')]")
    private HtmlElement loginLink;

    @Name("Имя пользователя")
    @FindBy(xpath = ".//span[contains(@class, 'username')]")
    private HtmlElement username;

    @Override
    @Step("Check user block")
    public HierarchicalErrorCollector validate(Validator<? extends TouchComTrMorda> validator) {
        if (validator.getUser() != null) {
            return collector()
                    .check(shouldSeeElement(this))
                    .check(validateUsername(validator));
        } else {
            return collector()
                    .check(shouldSeeElement(this))
                    .check(validateLoginLink(validator));
        }
    }

    @Step("Check login link")
    public HierarchicalErrorCollector validateLoginLink(Validator<? extends TouchComTrMorda> validator) {
        return collector()
                .check(shouldSeeElement(loginLink))
                .check(shouldSeeElementMatchingTo(loginLink,
                        hasText(getTranslation(HEAD_ENTER, Language.TR))));

    }

    @Step("Check username")
    public HierarchicalErrorCollector validateUsername(Validator<? extends TouchComTrMorda> validator) {
        return collector()
                .check(shouldSeeElement(username))
                .check(shouldSeeElementMatchingTo(username, hasText(validator.getUser().getLogin())));
    }

    @Override
    public HtmlElement getLoginLink() {
        return loginLink;
    }

    @Override
    public HtmlElement getUsername() {
        return username;
    }


}
