package ru.yandex.autotests.mordabackend.firefox.stocks;

import org.hamcrest.Matcher;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.stocksblock.Lite;
import ru.yandex.autotests.mordabackend.beans.stocksblock.StocksBlock;
import ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.StocksEntry;
import ru.yandex.autotests.utils.morda.BaseProperties;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.util.List;
import java.util.Map;

import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.index;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.lessThan;
import static org.hamcrest.Matchers.startsWith;
import static org.junit.Assume.assumeFalse;
import static ru.yandex.autotests.mordabackend.stocks.StockUtils.VALUE_LONG_MATCHER;
import static ru.yandex.autotests.mordabackend.stocks.StockUtils.VALUE_SHORT_MATCHER;
import static ru.yandex.autotests.mordabackend.stocks.StockUtils.getFirefoxStockEntries;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldMatchTo;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.addLink;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.normalizeUrl;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.region.Region.ISTANBUL;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.autotests.utils.morda.url.Domain.UA;
import static ru.yandex.qatools.matchers.collection.HasSameItemsAsCollectionMatcher.hasSameItemsAsCollection;

/**
 * User: ivannik
 * Date: 24.06.2014
 */
@Aqua.Test(title = "Firefox Stocks")
@Features("Firefox")
@Stories("Firefox Stocks")
@RunWith(CleanvarsParametrizedRunner.class)
public class FirefoxStocksTest {
    private static final Properties CONFIG = new Properties();

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(new BaseProperties.MordaEnv(CONFIG.getMordaEnv().getEnv().replace("www-", "firefox-")),
                    RU, UA, COM_TR)
                    .withLanguages(Language.RU, Language.UK, Language.BE, Language.KK, Language.TT)
                    .withUserAgents(FF_34)
                    .withCleanvarsBlocks(CleanvarsBlock.STOCKS, CleanvarsBlock.MORDA_CONTENT);

    private final Client client;
    private Region region;
    private Language language;
    private UserAgent userAgent;
    private Cleanvars cleanvars;

    public FirefoxStocksTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                             Language language, UserAgent userAgent) {
        this.region = region;
        this.language = language;
        this.client = client;
        this.userAgent = userAgent;
        this.cleanvars = cleanvars;
    }

    @Test
    public void stocksCount() {
        List<String> expectedStockIds =
                extract(getFirefoxStockEntries(region), on(StocksEntry.class).getId());
        List<String> actualStockIds = extract(cleanvars.getStocks().getLite(), on(Lite.class).getId());

        shouldMatchTo(actualStockIds, hasSameItemsAsCollection(expectedStockIds));
    }

    @Test
    public void stocksLiteFields() {
        Matcher<String> valueMatcher;
        if (region.equals(ISTANBUL)) {
            valueMatcher = VALUE_LONG_MATCHER;
        } else {
            valueMatcher = VALUE_SHORT_MATCHER;
        }

        Map<String, Lite> lites = index(cleanvars.getStocks().getLite(), on(Lite.class).getId());
        for (StocksEntry stocksEntry : getFirefoxStockEntries(region)) {

            shouldHaveParameter("Incorrect field 'text'", lites.get(stocksEntry.getId()).getText().replace(' ', ' '),
                    equalTo(getTranslation("home", "rates", "stocks." + stocksEntry.getId() + ".short", language)));

            if (!region.equals(KIEV) && !region.equals(ISTANBUL)) {
                shouldHaveParameter("Incorrect field 'alt'", lites.get(stocksEntry.getId()).getAlt(),
                        startsWith(getTranslation("home", "rates", "stocks." + stocksEntry.getId() + ".source", language)));
            }

            shouldHaveParameter("\"Incorrect field 'value'\"",
                    lites.get(stocksEntry.getId()).getValue(), valueMatcher);

        }
    }

    @Test
    public void stocksLiteHref() throws IOException {
        assumeFalse("Нет ссылок на мобильной .com.tr", userAgent.isMobile() && region.getDomain().equals(COM_TR));
        for (Lite lite : cleanvars.getStocks().getLite()) {
            String url = normalizeUrl(lite.getHref());
            addLink(url, region, false, language, userAgent);
            shouldHaveResponseCode(client, url, userAgent, lessThan(400));
        }
    }

    @Test
    public void showFlag() {
        shouldHaveParameter(cleanvars.getStocks(), having(on(StocksBlock.class).getShow(), equalTo(1)));
    }
}
