package ru.yandex.autotests.turkey.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: ivannik
 * Date: 14.09.2014
 */
@FindBy(xpath = "//div[contains(@class, 'b-line__informers')]")
@Name("Informers")
public class InformersBlock extends HtmlElement {

    @Name("Ссылка информера 'Регион'")
    @FindBy(xpath = "./span[contains(@class, 'informers')]/span[1]/a")
    public HtmlElement regionInformerLink;

    @Name("Ссылка информера 'Погода'")
    @FindBy(xpath = "./span[contains(@class, 'informers')]/span[2]/a")
    public InformerLink weatherInformerLink;

    @Name("Ссылка информера 'Пробки'")
    @FindBy(xpath = "./span[contains(@class, 'informers')]/span[3]/a")
    public InformerLink trafficInformerLink;

    @Name("Ссылка информера 'Курс USD'")
    @FindBy(xpath = "./span[contains(@class, 'informers')]/span[4]//a")
    public HtmlElement USDInformerLink;

    @Name("Ссылка информера 'Курс EUR'")
    @FindBy(xpath = "./span[contains(@class, 'informers')]/span[5]//a")
    public HtmlElement EURInformerLink;

    public static class InformerLink extends HtmlElement {

        @Name("Иконка информера")
        @FindBy(xpath = "./span[contains(@class, 'ico')]")
        public HtmlElement icon;
    }
}
