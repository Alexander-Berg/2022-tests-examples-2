package ru.yandex.autotests.morda.pages.common.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldExistElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.CONTENT;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 14/04/15
 */
@FindBy(xpath = "//head")
public abstract class OpenGraphBlock extends HtmlElement implements Validateable {

    @Name("Meta og:title")
    @FindBy(xpath = ".//meta[contains(@property, 'og:title')]")
    private HtmlElement ogTitle;

    @Name("Meta og:type")
    @FindBy(xpath = ".//meta[contains(@property, 'og:type')]")
    private HtmlElement ogType;

    @Name("Meta og:image")
    @FindBy(xpath = ".//meta[contains(@property, 'og:image')]")
    private HtmlElement ogImage;

    @Name("Meta og:site_name")
    @FindBy(xpath = ".//meta[contains(@property, 'og:site_name')]")
    private HtmlElement ogSiteName;

    @Name("Meta og:locale")
    @FindBy(xpath = ".//meta[contains(@property, 'og:locale')]")
    private HtmlElement ogLocale;

    @Name("Meta og:description")
    @FindBy(xpath = ".//meta[contains(@property, 'og:description')]")
    private HtmlElement ogDescription;

    public HierarchicalErrorCollector validate() {
        return collector()
                .check(
                        validateOgDescription(),
                        validateOgImage(),
                        validateOgLocale(),
                        validateOgSiteName(),
                        validateOgTitle(),
                        validateOgType()
                );
    }

    @Step
    public HierarchicalErrorCollector validateOgType() {
        return collector()
                .check(shouldExistElement(ogType))
                .check(shouldSeeElementMatchingTo(ogType, hasAttribute(CONTENT, equalTo("website"))));
    }

    @Step
    public abstract HierarchicalErrorCollector validateOgTitle();

    @Step
    public abstract HierarchicalErrorCollector validateOgImage();

    @Step
    public abstract HierarchicalErrorCollector validateOgSiteName();

    @Step
    public abstract HierarchicalErrorCollector validateOgLocale();

    @Step
    public abstract HierarchicalErrorCollector validateOgDescription();

    public HtmlElement getOgTitle() {
        return ogTitle;
    }

    public HtmlElement getOgType() {
        return ogType;
    }

    public HtmlElement getOgImage() {
        return ogImage;
    }

    public HtmlElement getOgSiteName() {
        return ogSiteName;
    }

    public HtmlElement getOgLocale() {
        return ogLocale;
    }

    public HtmlElement getOgDescription() {
        return ogDescription;
    }
}
