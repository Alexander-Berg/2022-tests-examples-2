package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: alex89
 * Date: 22.06.12
 */

@FindBy(xpath = "//div[contains(@id,'wd-_etrains')]")
@Name("Блок электричек")
public class EtrainsBlock extends Widget {

    @Name("Ссылка-заголовок 'Электрички'")
    @FindBy(xpath = ".//div[@class='b-content-item__title']/a")
    public HtmlElement eHeader;


    @Name("Направление")
    @FindBy(xpath = ".//div[@class='b-etrains__track']/div/a")
    public HtmlElement direction;

    @Name("Список с временами отправления")
    @FindBy(xpath = ".//div[@class='b-etrains__track']/ul[contains(@class,'times')]/li/a")
    public List<HtmlElement> timeTable;

    // @Required
    // @Name("Текст 'в ближайшие сутки электричек нет'")
    // @FindBy(xpath = ".//div[contains(@class,'info')]")
    // public HtmlElement infoText;
}