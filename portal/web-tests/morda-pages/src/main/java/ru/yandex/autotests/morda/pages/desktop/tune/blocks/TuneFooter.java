package ru.yandex.autotests.morda.pages.desktop.tune.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithFooter;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.autotests.utils.morda.language.Dictionary.Tune.Common;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.CoreMatchers.containsString;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslationSafely;
import static ru.yandex.qatools.htmlelements.matchers.WebElementMatchers.hasText;

/**
 * User: asamar
 * Date: 15.08.16
 */
@Name("Кнопка \"Сохранить\"")
@FindBy(xpath = "//div[@class = 'tune-footer']")
public class TuneFooter extends HtmlElement implements Validateable<Morda<? extends PageWithFooter<TuneFooter>>> {

    @Name("Мобильная версия")
    @FindBy(xpath = ".//a")
    public HtmlElement mobileVersion;

    @Name("Фидбек")
    @FindBy(xpath = ".//a[@data-statlog = 'feedback']")
    public HtmlElement feedback;

    @Name("Помощь")
    @FindBy(xpath = ".//a[@data-statlog = 'help']")
    public HtmlElement help;

    @Name("Копирайт")
    @FindBy(xpath = ".//div[@class = 'tune-footer__right']")
    public HtmlElement copyrights;

    @Step("{0}")
    private HierarchicalErrorCollector validateMobileLink(HtmlElement mobileVersion,
                                                          Validator<? extends Morda<? extends PageWithFooter<TuneFooter>>> validator) {
        return collector()
                .check(shouldSeeElement(mobileVersion))
                .check(
                        shouldSeeElementMatchingTo(mobileVersion,
                                hasText(getTranslationSafely(Common.MOBILE, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateCopyrights(HtmlElement copyrights,
                                                          Validator<? extends Morda<? extends PageWithFooter<TuneFooter>>> validator) {
        return collector()
                .check(shouldSeeElement(copyrights))
                .check(
                        shouldSeeElementMatchingTo(copyrights,
                                hasText(containsString("© " + getTranslationSafely(Common.COPYRIGHT, validator.getMorda().getLanguage()))))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateHelp(HtmlElement help,
                                                    Validator<? extends Morda<? extends PageWithFooter<TuneFooter>>> validator){
        return collector()
                .check(shouldSeeElement(help))
                .check(
                        shouldSeeElementMatchingTo(help,
                                hasText(getTranslationSafely(Common.HELP, validator.getMorda().getLanguage())))
                );
    }

    @Step("{0}")
    private HierarchicalErrorCollector validateFeedback(HtmlElement feedback,
                                                        Validator<? extends Morda<? extends PageWithFooter<TuneFooter>>> validator){
        return collector()
                .check(shouldSeeElement(feedback))
                .check(
                        shouldSeeElementMatchingTo(feedback,
                                hasText(getTranslationSafely(Common.FEEDBACK, validator.getMorda().getLanguage())))
                );
    }

    @Override
    @Step("Validate footer")
    public HierarchicalErrorCollector validate(Validator<? extends Morda<? extends PageWithFooter<TuneFooter>>> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateMobileLink(mobileVersion, validator),
                        validateCopyrights(copyrights, validator),
                        validateHelp(help, validator)
//                        validateFeedback(feedback, validator)
                );
    }
}
