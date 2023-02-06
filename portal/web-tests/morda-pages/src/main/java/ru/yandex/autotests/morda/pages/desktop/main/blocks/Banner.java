package ru.yandex.autotests.morda.pages.desktop.main.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

@Name("Баннер")
@FindBy(xpath = "//div[@id='banner']")
public class Banner extends HtmlElement {

    @Name("Flash объект")
    @FindBy(xpath = ".//object")
    public HtmlElement flashObject;

    @Name("Параметр movie баннера")
    @FindBy(xpath = ".//param[@name='movie']")
    public HtmlElement movieParam;

    @Name("Ссылка баннера")
    @FindBy(xpath = ".//a")
    public HtmlElement url;

    @Name("Параметр flashvars баннера")
    @FindBy(xpath = ".//param[@name='flashvars']")
    public HtmlElement flashParam;
}
