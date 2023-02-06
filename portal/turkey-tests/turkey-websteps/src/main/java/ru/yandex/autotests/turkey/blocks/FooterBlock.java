package ru.yandex.autotests.turkey.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: alex89
 * Date: 04.10.12
 */
@FindBy(xpath = "//div[contains(@class, 'b-line__mfooter')]")
@Name("Footer")
public class FooterBlock extends HtmlElement {

    @Name("Ссылка на турецкий сайт компании яндекса")
    @FindBy(xpath = ".//a[3]")
    public HtmlElement companyLink;

    @Name("Ссылка 'Оставить отзыв'")
    @FindBy(xpath = ".//a[4]")
    public HtmlElement feedbackLink;

    @Name("Копирайт")
    @FindBy(xpath = ".//span")
    public HtmlElement copyrightText;

    @Name("Ссылка на legal")
    @FindBy(xpath = ".//a[2]")
    public HtmlElement legalLink;

    @Name("Ссылка на страницу всех сервисов")
    @FindBy(xpath = ".//a[5]")
    public HtmlElement servicesLink;

    @Name("Ссылка на установку дефолтного поиска")
    @FindBy(xpath = ".//a[1]")
    public HtmlElement defaultSearchLink;

    @Name("Ссылка 'вернуть старый дизайн'")
    @FindBy(xpath = ".//a[@class='link reset__link reset__link_mode_default']")
    public HtmlElement setDefaultLink;
}
