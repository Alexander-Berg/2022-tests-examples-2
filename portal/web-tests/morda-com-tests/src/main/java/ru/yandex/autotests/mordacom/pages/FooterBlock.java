package ru.yandex.autotests.mordacom.pages;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: eoff
 * Date: 16.11.12
 */
@FindBy(xpath = "//div[contains(@class, 'b-line__mfooter')]")
@Name("Footer")
public class FooterBlock extends HtmlElement {

    @Name("Ссылка 'Technologies'")
    @FindBy(xpath = "./a[1]")
    public HtmlElement technologiesLink;

    @Name("Ссылка 'About Yandex'")
    @FindBy(xpath = "./a[2]")
    public HtmlElement aboutLink;

    @Name("Ссылка 'Terms of Service'")
    @FindBy(xpath = "./a[3]")
    public HtmlElement termsOfServiceLink;

    @Name("Ссылка 'Privacy Policy'")
    @FindBy(xpath = "./a[4]")
    public HtmlElement privacyLink;

    @Name("Ссылка 'Copyright Notice'")
    @FindBy(xpath = "./a[6]")
    public HtmlElement copyrightLink;

    @Name("Копирайт")
    @FindBy(xpath = ".//span")
    public HtmlElement copyrightText;

}
