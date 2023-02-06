package ru.yandex.autotests.morda.pages.desktop.com.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.com.DesktopComMorda;
import ru.yandex.autotests.morda.pages.desktop.com.htmlelements.HeaderUnauthorized;
import ru.yandex.autotests.morda.pages.desktop.com.htmlelements.HeaderAuthorized;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithLoginLink;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollector.collector;

/**
 * User: asamar
 * Date: 29.09.2015.
 */
@Name("Хедер")
@FindBy(xpath = "//div[contains(@class, 'b-line__bar-right')]")
public class HeaderBlock extends HtmlElement implements BlockWithLoginLink, Validateable<DesktopComMorda> {

    private HeaderUnauthorized headerUnauthorized;
    private HeaderAuthorized headerAuthorized;

    @Override
    public HtmlElement getLoginLink() {
        return null;
    }

    @Override
    public HierarchicalErrorCollector validate(Validator<? extends DesktopComMorda> validator) {
        return validator.getUser() == null ?
                collector()
                        .check(headerUnauthorized.validate(validator)):
                collector()
                        .check(headerAuthorized.validate(validator));
    }


}
