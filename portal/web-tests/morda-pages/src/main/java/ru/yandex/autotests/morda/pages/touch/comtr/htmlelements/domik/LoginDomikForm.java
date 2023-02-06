package ru.yandex.autotests.morda.pages.touch.comtr.htmlelements.domik;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.comtr.TouchComTrMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.morda.steps.CheckSteps;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.autotests.utils.morda.language.Dictionary;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.PLACEHOLDER;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 31/03/15
 */
@Name("Блок для залогина")
@FindBy(xpath = ".//div[contains(@class, 'mdomik__content')]")
public class LoginDomikForm extends HtmlElement implements Validateable<TouchComTrMorda> {

    private static final CheckSteps CHECK_STEPS = new CheckSteps();

    @Name("Поле \"Логин\"")
    @FindBy(xpath = ".//input[@name='login']")
    private TextInput login;

    @Name("Поле \"Пароль\"")
    @FindBy(xpath = ".//input[@name='passwd']")
    private TextInput password;

    @Name("Кнопка \"Войти\"")
    @FindBy(xpath = ".//button[@type='submit']")
    private HtmlElement loginButton;

    @Override
    @Step("Check login domik form")
    public HierarchicalErrorCollector validate(Validator<? extends TouchComTrMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateLogin(validator),
                        validatePassword(validator),
                        validateLoginButton(validator)
                );
    }

    @Step("Check login field")
    public HierarchicalErrorCollector validateLogin(Validator<? extends TouchComTrMorda> validator) {
        return collector()
                .check(shouldSeeElement(login))
                .check(shouldSeeElementMatchingTo(login,
                        hasAttribute(PLACEHOLDER, equalTo(getTranslation(Dictionary.Home.Mail.LOGIN_LABEL_UP, Language.TR)))
                ));
    }

    @Step("Check password field")
    public HierarchicalErrorCollector validatePassword(Validator<? extends TouchComTrMorda> validator) {
        return collector()
                .check(shouldSeeElement(password))
                .check(shouldSeeElementMatchingTo(password,
                        hasAttribute(PLACEHOLDER, equalTo(getTranslation(Dictionary.Home.Mail.PASSWD_UP, Language.TR)))
                ));
    }

    @Step("Check login button")
    public HierarchicalErrorCollector validateLoginButton(Validator<? extends TouchComTrMorda> validator) {
        return collector()
                .check(shouldSeeElement(loginButton))
                .check(shouldSeeElementMatchingTo(loginButton,
                        hasText(getTranslation(Dictionary.Home.Mail.LOGIN, Language.TR))
                ));
    }

    public TextInput getLogin() {
        return login;
    }

    public TextInput getPassword() {
        return password;
    }

    public HtmlElement getLoginButton() {
        return loginButton;
    }

}
