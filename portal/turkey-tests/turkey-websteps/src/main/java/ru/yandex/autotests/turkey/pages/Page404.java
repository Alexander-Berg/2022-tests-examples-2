package ru.yandex.autotests.turkey.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: eoff
 * Date: 07.02.13
 */
public class Page404 {
    public Page404(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @Name("Лого Яндекса")
    @FindBy(xpath = "//div[contains(@class, 'layout__line_top')]//a[contains(@class, 'logo')]")
    public HtmlElement logo;

    @Name("Поисковая строка")
    @FindBy(xpath = "//input[@name='text']")
    public TextInput input;

    @Name("Кнопка 'Найти'")
    @FindBy(xpath = "//button[@type='submit']")
    public HtmlElement searchButton;

    @Name("Сообщение об ошибке")
    @FindBy(xpath = "//h1[contains(@class, 'content__title')]")
    public HtmlElement errorMessage;

    @Name("Обратная связь")
    @FindBy(xpath = "//h1[contains(@class, 'content__title')]/../div[1]")
    public HtmlElement feedbackMessage;

    @Name("Ссылка на feedback")
    @FindBy(xpath = "//h1[contains(@class, 'content__title')]/../div[1]/a")
    public HtmlElement feedbackLink;

    @Name("Ссылка Sirket")
    @FindBy(xpath = "//div[@class='foot']/a[1]")
    public HtmlElement sirketLink;

    @Name("Ссылка Company")
    @FindBy(xpath = "//div[@class='foot']/a[2]")
    public HtmlElement companyLink;

    @Name("Ссылка на Яндекс")
    @FindBy(xpath = "//div[@class='foot']/a[3]")
    public HtmlElement yandexLink;
}
