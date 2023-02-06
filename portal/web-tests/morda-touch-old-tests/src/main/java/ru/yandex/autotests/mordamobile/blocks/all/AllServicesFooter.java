package ru.yandex.autotests.mordamobile.blocks.all;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

@Name("Футер")
@FindBy(xpath = "//div[contains(@class, 'b-line__footer')]")
public class AllServicesFooter extends HtmlElement {
    @Name("Ссылка помощь")
    @FindBy(xpath = ".//div[contains(@class,'footer__link_help')]//a")
    public HtmlElement helpLink;

    @Name("Ссылка компании")
    @FindBy(xpath = ".//div[contains(@class,'footer__link_company')]//a")
    public HtmlElement companyLink;

    @Name("Ссылка на главную")
    @FindBy(xpath = ".//div[contains(@class,'footer__link_yandex')]//a")
    public HtmlElement yandexLink;
}