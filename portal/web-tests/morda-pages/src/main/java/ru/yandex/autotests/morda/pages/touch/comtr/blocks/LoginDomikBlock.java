package ru.yandex.autotests.morda.pages.touch.comtr.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.comtr.TouchComTrMorda;
import ru.yandex.autotests.morda.pages.touch.comtr.htmlelements.domik.LoginDomikButtons;
import ru.yandex.autotests.morda.pages.touch.comtr.htmlelements.domik.LoginDomikForm;
import ru.yandex.autotests.morda.pages.touch.comtr.htmlelements.domik.LoginDomikSocial;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 09/04/15
 */
@Name("Домик")
@FindBy(xpath = "//div[contains(@class, 'mdomik__body')]")
public class LoginDomikBlock extends HtmlElement implements Validateable<TouchComTrMorda> {

    private LoginDomikButtons loginDomikButtons;

    private LoginDomikSocial loginDomikSocial;

    private LoginDomikForm loginDomikForm;

    @Override
    @Step("Check domik")
    public HierarchicalErrorCollector validate(Validator<? extends TouchComTrMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        loginDomikButtons.validate(validator),
                        loginDomikSocial.validate(validator),
                        loginDomikForm.validate(validator)
                );
    }

    public LoginDomikButtons getLoginDomikButtons() {
        return loginDomikButtons;
    }

    public LoginDomikSocial getLoginDomikSocial() {
        return loginDomikSocial;
    }

    public LoginDomikForm getLoginDomikForm() {
        return loginDomikForm;
    }


}
