package ru.yandex.autotests.tunewebtests.responses;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 08.06.13
 */

import org.apache.http.HttpResponse;
import org.apache.http.StatusLine;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.params.CookiePolicy;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.util.EntityUtils;
import org.apache.log4j.Logger;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.aqua.annotations.project.Feature;
import ru.yandex.autotests.tunewebtests.pages.HomePage;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.selenium.grid.GridClient;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.lessThanOrEqualTo;

@Aqua.Test(title = "Проверка отсутсвия ссылок с 404-ой ошибкой на тюне")
@Feature("Ссылки на Тюне")
@RunWith(Parameterized.class)
public class TuneLinksTest {
    private static final Logger LOG = Logger.getLogger(TuneLinksTest.class);

    private HttpClient httpClient = createHttpClient();

    public static DefaultHttpClient createHttpClient() {
        DefaultHttpClient client = new DefaultHttpClient();
        client.getParams().setParameter("http.protocol.single-cookie-header", true);
        client.getParams().setParameter("http.protocol.cookie-policy", CookiePolicy.BROWSER_COMPATIBILITY);
        client.getParams().setParameter("http.useragent",
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:10.0.1) Gecko/20100101 Firefox/10.0.1");
        return client;
    }

    private static final String TUNE_URL_PATTERN = "http://tune.yandex%s";

    @Parameterized.Parameters
    public static Collection<Object[]> data() throws Exception {
        WebDriver driver = new GridClient().find(DesiredCapabilities.htmlUnit());
        HomePage homePage = new HomePage(driver);
        final List<Object[]> result = new ArrayList<Object[]>();
        for (Domain d : Domain.values()) {
            final Set<String> links = new HashSet<String>();
            String url = String.format(TUNE_URL_PATTERN, d);
            driver.get(url);
            for (HtmlElement element : homePage.allLinks) {
                links.add(element.getAttribute("href"));
            }
            for (String link : links) {
                result.add(new Object[]{url, link});
            }
        }
        driver.quit();

        return result;
    }

    private String tuneUrl;
    private String link;

    public TuneLinksTest(String tuneUrl, String link) {
        this.tuneUrl = tuneUrl;
        this.link = link;
    }

    @Test
    public void linkResponse() throws Exception {
        HttpGet httpGet = new HttpGet(link);
        httpGet.addHeader("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8");
        LOG.info(tuneUrl + " >> " + link);
        StatusLine status = executeHttpGet(httpGet);
        LOG.info(tuneUrl + " >> " + link + " >> " + status);
        assertThat("По '" + link + "' код ответа: " + status, status.getStatusCode(), lessThanOrEqualTo(400));
    }

    private StatusLine executeHttpGet(HttpGet httpGet) throws IOException {
        HttpResponse response = httpClient.execute(httpGet);
        StatusLine status = response.getStatusLine();
        EntityUtils.consume(response.getEntity());
        return status;
    }
}
