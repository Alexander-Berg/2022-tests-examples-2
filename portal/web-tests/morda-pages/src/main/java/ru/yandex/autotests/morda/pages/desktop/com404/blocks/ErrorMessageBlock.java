package ru.yandex.autotests.morda.pages.desktop.com404.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.com404.Com404Morda;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static java.lang.String.format;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: asamar
 * Date: 06.10.2015.
 */
@Name("Сообщение об ошибке")
@FindBy(xpath = "//div[contains(@class, 'layout__content')]")
public class ErrorMessageBlock extends HtmlElement implements Validateable<Com404Morda> {

    @Name("Текст сообщения об ошибке")
    @FindBy(xpath = ".//h1")
    private HtmlElement errorText;

    @Name("Фидбек")
    @FindBy(xpath = ".//div")
    private Feedback feedBack;

    public static class Feedback extends HtmlElement {

        @Name("Ссылка на фидбек")
        @FindBy(xpath = "./a")
        public HtmlElement feedbackLink;
    }


    @Override
    @Step("Check ErrorMessage block")
    public HierarchicalErrorCollector validate(Validator<? extends Com404Morda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(validateErrorText(errorText, validator))
                .check(validateFeedbackLink(feedBack, validator));
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateErrorText(HtmlElement errorText,
                                                               Validator<? extends Com404Morda> validator) {
        return collector()
                .check(shouldSeeElement(errorText))
                .check(shouldSeeElementMatchingTo(errorText,
                        hasText(getTranslation(
                                "home",
                                "error404_spok_yes",
                                "nopage_full",
                                validator.getMorda().getLanguage()))));
    }

    @Step("{0}")
    public static HierarchicalErrorCollector validateFeedbackLink(Feedback feedBack,
                                                                  Validator<? extends Com404Morda> validator) {
        String feedBackTextTranslation = getTranslation(
                "home",
                "error404_spok_yes",
                "special_bad3",
                validator.getMorda().getLanguage()).replace("  "," ");

        String contactUsTranslation = getTranslation(
                "home",
                "error404_spok_yes",
                "contact_us",
                validator.getMorda().getLanguage());

        return collector()
                .check(shouldSeeElement(feedBack))
                .check(
                        shouldSeeElementMatchingTo(feedBack,
                                hasText(format(feedBackTextTranslation, contactUsTranslation))),
                        shouldSeeElementMatchingTo(feedBack.feedbackLink,
                                hasAttribute(HREF, startsWith("https://yandex.com/support/not-found/?form1969-url404")))
                );
    }
}
