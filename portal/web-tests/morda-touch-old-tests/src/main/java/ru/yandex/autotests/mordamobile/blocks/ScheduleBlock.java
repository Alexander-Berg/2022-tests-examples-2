package ru.yandex.autotests.mordamobile.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
@Name("Блок расписания")
@FindBy(xpath = "//div[contains(@class, 'b-widget  b-rasp')]")
public class ScheduleBlock extends HtmlElement {
    @Name("Иконка")
    @FindBy(xpath = ".//i")
    public HtmlElement icon;

    @Name("Заголовок")
    @FindBy(xpath = ".//a[contains(@class,'b-widget__title')]")
    public HtmlElement title;

    @Name("Элементы в расписании")
    @FindBy(xpath = ".//a[@class='b-link']")
    public List<ScheduleItem> allItems;

    public static class ScheduleItem extends HtmlElement {
        @Name("Иконка")
        @FindBy(xpath = ".//div[contains(@class,'b-rasp__icon')]")
        public HtmlElement icon;
    }
}
