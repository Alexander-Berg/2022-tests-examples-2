package ru.yandex.autotests.mainmorda.steps;

import org.apache.http.HttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.DefaultHttpClient;
import org.hamcrest.Matcher;
import org.hamcrest.text.IsEqualIgnoringCase;
import org.openqa.selenium.WebDriver;
import org.w3c.dom.Document;
import org.xml.sax.SAXException;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.users.User;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import java.io.IOException;
import java.util.List;

import static ch.lambdaj.Lambda.on;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.allOf;
import static org.junit.Assert.fail;
import static ru.yandex.autotests.mainmorda.blocks.PageBlock.HEADER;
import static ru.yandex.qatools.htmlelements.matchers.common.HasTextMatcher.hasText;

/**
 * User: lipka
 * Date: 26.06.13
 */
public class HeaderSteps {

    public static final String LANGFIELD = "dbfield";

    private WebDriver driver;
    private CommonMordaSteps userSteps;
    private LinksSteps userLink;

    public HeaderSteps(WebDriver driver) {
        this.driver = driver;
        this.userSteps = new CommonMordaSteps(driver);
        this.userLink = new LinksSteps(driver);
    }

    @Step
    public void shouldSeePassportLang(Language language, User user) throws IOException, ParserConfigurationException,
            SAXException {
        HttpGet httpGet = new HttpGet("http://blackbox-mimino.yandex.net/blackbox/?method=userinfo&login=" +
                user.getLogin() + "&userip=127.0.0.1&dbfields=userinfo.lang.uid");
        httpGet.addHeader("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8");
        DefaultHttpClient client = new DefaultHttpClient();
        HttpResponse response = client.execute(httpGet);
        DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
        DocumentBuilder db = dbf.newDocumentBuilder();
        Document doc = db.parse(response.getEntity().getContent());
        doc.getDocumentElement().normalize();
        String passportLang = doc.getElementsByTagName(LANGFIELD).item(0).getTextContent();
        assertThat(passportLang, IsEqualIgnoringCase.equalToIgnoringCase(language.toString()));
    }

    @Step
    public void shouldSeeAllLinks(List<HtmlElement> elementList, LinkInfo link) {
        for (HtmlElement element : elementList) {
            userLink.shouldSeeLink(element, link, HEADER);
        }
    }

    @Step
    public <T extends HtmlElement> T findElementInList(List<T> list, Matcher<? super T> matcher) {
        for (T element : list) {
            if (matcher.matches(element)) {
                return element;
            }
        }
        fail("Элемент не найден в списке");
        return null;
    }

    @Step
    public void shouldSeeLinkIn(List<? extends HtmlElement> list, LinkInfo linkInfo) {
        HtmlElement linkElement = userSteps.shouldSeeElementInList(list, on(HtmlElement.class),
                allOf(hasText(linkInfo.text), linkInfo.attributes));
        userLink.shouldSeeLink(linkElement, linkInfo, HEADER);
    }

    @Step
    public void shouldSeeLinkWithoutClickIn(List<? extends HtmlElement> list, LinkInfo linkInfo) {
        HtmlElement linkElement = userSteps.shouldSeeElementInList(list, on(HtmlElement.class),
                allOf(hasText(linkInfo.text), linkInfo.attributes));
        userSteps.shouldSeeLinkLight(linkElement, linkInfo);
    }
}
