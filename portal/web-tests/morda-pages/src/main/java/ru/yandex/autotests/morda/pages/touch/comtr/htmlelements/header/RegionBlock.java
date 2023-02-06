package ru.yandex.autotests.morda.pages.touch.comtr.htmlelements.header;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithLocateIcon;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithRegionName;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.comtr.TouchComTrMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.Matchers.containsString;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.CLASS;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 31/03/15
 */
@Name("Блок с названием региона")
@FindBy(xpath = "//div[contains(@class, 'mheader__locate')]")
public class RegionBlock extends HtmlElement implements BlockWithRegionName, BlockWithLocateIcon,
        Validateable<TouchComTrMorda> {

    @Name("Иконка определения региона")
    @FindBy(xpath = ".//div[contains(@class, 'locate-icon')]")
    private HtmlElement locateIcon;

    @Name("Регион с датой")
    @FindBy(xpath = ".//span[contains(@class, 'locate-text')]")
    private HtmlElement regionName;

    @Override
    @Step("Check region block")
    public HierarchicalErrorCollector validate(Validator<? extends TouchComTrMorda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(
                        validateLocateIcon(validator),
                        validateRegionName(validator)
                );
    }

    @Step("Check locateButton icon")
    public HierarchicalErrorCollector validateLocateIcon(Validator<? extends TouchComTrMorda> validator) {
        return collector()
                .check(shouldSeeElement(locateIcon))
                .check(shouldSeeElementMatchingTo(locateIcon,
                        hasAttribute(CLASS, containsString("geobutton_size_s"))));
    }

    @Step("Check region name and date")
    public HierarchicalErrorCollector validateRegionName(Validator<? extends TouchComTrMorda> validator) {
        String month = validator.getCleanvars().getBigShortMonth();
        return collector()
                .check(shouldSeeElement(regionName))
                .check(shouldSeeElementMatchingTo(regionName,
                        hasText(matches("\\d+ " + month + ", " + validator.getMorda().getRegion().getName()))));
    }

    @Override
    public HtmlElement getLocateIcon() {
        return locateIcon;
    }

    @Override
    public HtmlElement getRegionBlock() {
        return regionName;
    }

}
