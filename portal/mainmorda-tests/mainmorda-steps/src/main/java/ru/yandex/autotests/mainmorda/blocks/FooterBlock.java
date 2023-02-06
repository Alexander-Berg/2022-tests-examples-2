package ru.yandex.autotests.mainmorda.blocks;

import org.openqa.selenium.support.FindBy;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

/**
 * User: alex89
 * Date: 17.07.12
 * Элементы footer-а на новой "морде".
 */

@FindBy(xpath = "//div[contains(@class,'b-line_foot')]")
@Name("Footer")
public class FooterBlock extends HtmlElement {
    @Name("Текст и ссылка 'Дизайн'")
    @FindBy(xpath = ".//div[@class='b-design']")
    public HtmlElement designTextAndLink;

    @Name("Ссылка 'Студия Артемия Лебедева'")
    @FindBy(xpath = ".//div[@class='b-design']/a")
    public HtmlElement artLebedevStudioLink;

    @Name("Ссылка 'Директ'")
    @FindBy(xpath = ".//div[contains(@class,'business')][1]/a[contains(@href,'direct')]")
    public HtmlElement directLink;

    @Name("Рекламное сообщение 'Директ'-а")
    @FindBy(xpath = ".//div[contains(@class,'business')][1]/a[contains(@href,'advertising')]")
    public HtmlElement directCommentLink;

    @Name("Ссылка 'Яндекс по умолчанию'")
    @FindBy(xpath = ".//div[contains(@class,'business')][3]/a")
    public HtmlElement yandexDefaultLink;

    @Name("Ссылка 'Метрика'")
    @FindBy(xpath = ".//a[contains(@href,'metrika')]")
    public HtmlElement metrikaLink;

    @Name("Ссылка 'Реклама'")
    @FindBy(xpath = ".//div[contains(@class,'business')][2]/a")
    public HtmlElement advLink;

    @Name("Ссылка 'Помощь'")
    @FindBy(xpath = ".//div[contains(@class,'b-footer__link_help')]/a")
    public HtmlElement helpLink;

    @Name("Ссылка 'Обратная связь'")
    @FindBy(xpath = ".//div[contains(@class,'b-footer__link_feedback')]/a")
    public HtmlElement feedbackLink;

    @Name("Ссылка 'О компании'")
    @FindBy(xpath = ".//div[contains(@class,'b-footer__link_company')]/a")
    public HtmlElement companyLink;

    @Name("Ссылка 'About'")
    @FindBy(xpath = ".//div[contains(@class,'b-footer__link_about')]/a")
    public HtmlElement aboutLink;

    @Name("Ссылка 'Вакансии'")
    @FindBy(xpath = ".//div[contains(@class,'b-footer__link_vacancies')]/a")
    public HtmlElement vacanciesLink;

    @Name("Текст с Копирайтом")
    @FindBy(xpath = ".//*[contains(@class, 'right')]//div[contains(@class,'b-footer__link')][last()]")
    public HtmlElement copyrightText;

    @Name("Ссылка 'Блог'")
    @FindBy(xpath = ".//div[contains(@class,'b-footer__link_blog')]/a")
    public HtmlElement blogLink;
}