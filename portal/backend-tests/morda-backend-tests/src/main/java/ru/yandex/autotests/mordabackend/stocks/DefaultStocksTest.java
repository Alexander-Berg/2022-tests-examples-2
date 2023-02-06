package ru.yandex.autotests.mordabackend.stocks;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.stocksblock.Lite;
import ru.yandex.autotests.mordabackend.beans.stocksblock.StocksBlock;
import ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.StocksEntry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.io.IOException;
import java.util.EnumSet;
import java.util.List;
import java.util.Map;

import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.index;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.lessThan;
import static org.junit.Assume.assumeFalse;
import static ru.yandex.autotests.mordabackend.stocks.StockUtils.STOCKS_REGIONS_ALL;
import static ru.yandex.autotests.mordabackend.stocks.StockUtils.VALUE_LONG_MATCHER;
import static ru.yandex.autotests.mordabackend.stocks.StockUtils.getStockEntries;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldMatchTo;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.addLink;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.normalizeUrl;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.url.Domain.BY;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;
import static ru.yandex.autotests.utils.morda.url.Domain.KZ;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.autotests.utils.morda.url.Domain.UA;
import static ru.yandex.qatools.matchers.collection.HasSameItemsAsCollectionMatcher.hasSameItemsAsCollection;

/**
 * User: ivannik
 * Date: 24.06.2014
 */
@Aqua.Test(title = "Default Stocks")
@Features("Stocks")
@Stories("Default Stocks")
@RunWith(CleanvarsParametrizedRunner.class)
public class DefaultStocksTest {

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(STOCKS_REGIONS_ALL)
                    .withLanguages(Language.RU, Language.UK, Language.BE, Language.KK, Language.TT)
                    .withUserAgents(FF_34)
                    .withCleanvarsBlocks(CleanvarsBlock.STOCKS, CleanvarsBlock.MORDA_CONTENT);

    private final Client client;
    private Region region;
    private Language language;
    private UserAgent userAgent;
    private Cleanvars cleanvars;

    public DefaultStocksTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                             Language language, UserAgent userAgent) {
        this.region = region;
        this.language = language;
        this.client = client;
        this.userAgent = userAgent;
        this.cleanvars = cleanvars;
    }

    @Before
    public void setUp() {
        assumeFalse("Нет блока Stocks на большой",
                userAgent.equals(FF_34) && EnumSet.of(KZ, UA, BY, RU).contains(region.getDomain()));
    }

    @Test
    public void stocksCount() {
        List<String> expectedStockIds =
                extract(getStockEntries(region, userAgent, cleanvars.getMordaContent()), on(StocksEntry.class).getId());
        List<String> actualStockIds = extract(cleanvars.getStocks().getLite(), on(Lite.class).getId());

        shouldMatchTo(actualStockIds, hasSameItemsAsCollection(expectedStockIds));
    }

    @Test
    public void stocksLiteFields() {
        Map<String, Lite> lites = index(cleanvars.getStocks().getLite(), on(Lite.class).getId());
        for (StocksEntry stocksEntry : getStockEntries(region, userAgent, cleanvars.getMordaContent())) {

            shouldHaveParameter("Incorrect field 'text'", lites.get(stocksEntry.getId()).getText().replace(' ', ' '),
                    equalTo(getTranslation("home", "rates", "stocks." + stocksEntry.getId() + ".short", language)));

            shouldHaveParameter("\"Incorrect field 'value'\"",
                    lites.get(stocksEntry.getId()).getValue(), VALUE_LONG_MATCHER);
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
