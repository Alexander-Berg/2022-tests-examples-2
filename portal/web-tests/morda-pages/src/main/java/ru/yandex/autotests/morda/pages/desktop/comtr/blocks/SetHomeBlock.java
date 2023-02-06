package ru.yandex.autotests.morda.pages.desktop.comtr.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSetHomeLink;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 17/04/15
 */
@Name("Блок \"Сделать стартовой\"")
@FindBy(xpath = "//div[contains(@class, 'b-sethome_type')]")
public class SetHomeBlock extends HtmlElement implements BlockWithSetHomeLink {

    @Name("Ссылка \"Сделать стартовой\"")
    @FindBy(xpath = ".//a[contains(@class, 'sethome__link')]")
    private HtmlElement setHomeLink;

    @Override
    public HtmlElement getSetHomeLink() {
        return setHomeLink;
    }
}
