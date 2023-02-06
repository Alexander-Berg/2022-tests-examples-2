package ru.yandex.autotests.hwmorda.pages;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.Button;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: alex89
 * Date: 13.09.12
 */
@FindBy(xpath = "//div[contains(@class,'foot')]")
@Name("Кнопки footer-a")
public class LgFooterPanel extends HtmlElement {
    @Name("Кнопка footer-a 'Выход'")
    @FindBy(xpath = ".//div[@nav-event='exit' and contains(.,'Выход')]")
    public Button exitButton;

    @Name("Кнопка footer-a 'Назад'")
    @FindBy(xpath = ".//div[@nav-event='back' and contains(.,'Назад')]")
    public Button backButton;

    //на Главной странице
    @Name("Кнопка footer-a 'Погода'")
    @FindBy(xpath = ".//div[@nav-event='red' and contains(.,'Погода')]")
    public Button weatherButton;

    @Name("Кнопка footer-a 'Новости'")
    @FindBy(xpath = ".//div[@nav-event='green' and contains(.,'Новости')]")
    public Button newsButton;

    @Name("Кнопка footer-a 'Телепрограмма'")
    @FindBy(xpath = ".//div[@nav-event='blue' and contains(.,'Телепрограмма')]")
    public Button tvButton;

    @Name("Кнопка footer-a 'Фото дня'")
    @FindBy(xpath = ".//div[@nav-event='yellow' and contains(.,'Фото дня')]")
    public Button photoButton;

    //На Под-странице
    @Name("Кнопка footer-a 'Слайд-шоу'")
    @FindBy(xpath = ".//div[@nav-event='yellow' and contains(.,'Слайд-шоу')]")
    public Button slideShowButton;

    @Name("Кнопка footer-a 'Главные новости'")
    @FindBy(xpath = ".//div[@nav-event='yellow' and contains(.,'Главные новости')]")
    public Button mainNewsButton;

    @Name("Кнопка footer-a 'Местные новости'")
    @FindBy(xpath = ".//div[@nav-event='yellow' and contains(.,'Местные новости')]")
    public Button regionalNewsButton;
}
