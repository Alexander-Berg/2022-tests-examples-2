package ru.yandex.autotests.morda.pages.desktop.hwlgV2.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.hwlgV2.DesktopHwLgV2Morda;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static javax.ws.rs.core.UriBuilder.fromUri;
import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElement;
import static ru.yandex.autotests.morda.steps.CheckSteps.shouldSeeElementMatchingTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.SRC;

/**
 * User: asamar
 * Date: 30.10.2015.
 */
@Name("Логотип")
@FindBy(xpath = "//img[@class='b-logo__main_img']")
public class LogoBlock extends HtmlElement implements Validateable<DesktopHwLgV2Morda> {

    @Override
    @Step("Validate Logo Block")
    public HierarchicalErrorCollector validate(Validator<? extends DesktopHwLgV2Morda> validator) {
        return collector()
                .check(shouldSeeElement(this))
                .check(shouldSeeElementMatchingTo(this,
                        hasAttribute(SRC, equalTo(fromUri(validator.getMorda().getUrl().toString())
                                .path("/img/b-logo__pos_main.png")
                                .build()
                                .toString()
                        )))
                );
    }
}
