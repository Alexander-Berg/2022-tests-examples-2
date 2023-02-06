package ru.yandex.autotests.mainmorda.pages;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.mordacommonsteps.utils.TextInput;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

import java.util.List;

/**
 * User: eoff
 * Date: 07.02.13
 */
public class Page404 {
    public Page404(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @Name("Текст 'Нет такой страницы'")
    @FindBy(xpath = "//h1[contains(@class, 'title')]")
    public HtmlElement noPageText;

    @Name("Лого Яндекса")
    @FindBy(xpath = "//div[contains(@class, 'layout__line_top')]//a[contains(@class, 'logo')]")
    public HtmlElement logo;

    @Name("Поисковая строка")
    @FindBy(xpath = "//input[@name='text']")
    public TextInput input;

    @Name("Кнопка 'Найти'")
    @FindBy(xpath = "//button[@type='submit']")
    public HtmlElement searchButton;

    @Name("Ссылка 'Напишите нам'")
    @FindBy(xpath = "//div[contains(@class, 'layout__content')]/div[1]//a")
    public HtmlElement feedbackLink;

    @Name("Ссылка на company.yandex.ru")
    @FindBy(xpath = "//div[@class='foot']/a[1]")
    public HtmlElement companyRuLink;

    @Name("Ссылка на company.yandex.com")
    @FindBy(xpath = "//div[@class='foot']/a[2]")
    public HtmlElement companyComLink;

    @Name("Ссылка на Яндекс")
    @FindBy(xpath = "//div[@class='foot']/a[3]")
    public HtmlElement yandexLink;

    @Name("Список сервисов")
    @FindBy(xpath = "//li[contains(@class, 'services__main-item')]")
    public List<Page404Service> services;


    public static class Page404Service extends HtmlElement {

        @Name("Иконка")
        @FindBy(xpath = ".//img[contains(@class, 'b-ico-service')]")
        public HtmlElement icon;


        @Name("Название сервиса")
        @FindBy(xpath = ".//a[contains(@class, 'title')]")
        public HtmlElement serviceName;

        @Name("Подпись")
        @FindBy(xpath = ".//a[contains(@class, 'link_black_yes')]")
        public HtmlElement serviceSign;

    }
}
