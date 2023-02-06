package ru.yandex.autotests.morda.pages.touch.comtr.htmlelements.domik;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.comtr.TouchComTrMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.utils.morda.language.Dictionary;
import ru.yandex.autotests.utils.morda.language.Language;
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
 * Date: 31/03/15
 */
@Name("Кнопки в домике")
@FindBy(xpath = ".//div[contains(@class, 'buttons')]")
public class LoginDomikButtons extends HtmlElement implements Validateable<TouchComTrMorda> {

    @Name("Кнопка \"Вспомнить пароль\"")
    @FindBy(xpath = ".//a[contains(@class, 'mdomik__rem')]")
    private HtmlElement rememberButton;

    @Name("Кнопка \"Зарегистрироваться\"")
    @FindBy(xpath = ".//a[contains(@class, 'mdomik__reg')]")
    private HtmlElement registerButton;

    @Override
    @Step("Check login domik buttons")
    public HierarchicalErrorCollector validate(Validator<? extends TouchComTrMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateRememberButton(validator),
                        validateRegisterButton(validator)
                );

    }

    @Step("Check remember link")
    public HierarchicalErrorCollector validateRememberButton(Validator<? extends TouchComTrMorda> validator) {
        return collector()
                .check(shouldSeeElement(rememberButton))
                .check(shouldSeeElementMatchingTo(rememberButton, allOfDetailed(
                        hasText(getTranslation(Dictionary.Home.Mobile.DOMIK_REMEMBER_PWD, Language.TR)),
                        hasAttribute(HREF, equalTo(validator.getMorda().getPassportUrl() + "passport?mode=restore"))
                )));
    }

    @Step("Check register button")
    public HierarchicalErrorCollector validateRegisterButton(Validator<? extends TouchComTrMorda> validator) {
        return collector()
                .check(shouldSeeElement(registerButton))
                .check(shouldSeeElementMatchingTo(registerButton, allOfDetailed(
                        hasText(getTranslation(Dictionary.Home.Mobile.DOMIK_REGISTER, Language.TR)),
                        hasAttribute(HREF, startsWith(validator.getMorda().getPassportUrl() +
                                "registration?mode=register"))
                )));
    }

    public HtmlElement getRememberButton() {
        return rememberButton;
    }

    public HtmlElement getRegisterButton() {
        return registerButton;
    }

}
