package ru.yandex.autotests.mordabackend.stocks;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.topnews.TopnewsStocksItem;
import ru.yandex.autotests.mordabackend.blocks.CleanvarsBlock;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils;
import ru.yandex.autotests.mordabackend.utils.runner.CleanvarsParametrizedRunner;
import ru.yandex.autotests.mordaexportsclient.beans.StocksEntry;
import ru.yandex.autotests.mordaexportsclient.beans.StocksFlatEntry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;
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
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.lessThan;
import static org.hamcrest.Matchers.startsWith;
import static org.junit.Assume.assumeFalse;
import static ru.yandex.autotests.mordabackend.stocks.StockUtils.STOCKS_REGIONS_ALL;
import static ru.yandex.autotests.mordabackend.stocks.StockUtils.VALUE_SHORT_MATCHER;
import static ru.yandex.autotests.mordabackend.stocks.StockUtils.getStocksFlatEntry;
import static ru.yandex.autotests.mordabackend.stocks.StockUtils.getTopnewsStockEntries;
import static ru.yandex.autotests.mordabackend.useragents.UserAgent.FF_34;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveParameter;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldHaveResponseCode;
import static ru.yandex.autotests.mordabackend.utils.CleanvarsUtils.shouldMatchTo;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.addLink;
import static ru.yandex.autotests.mordabackend.utils.LinkUtils.normalizeUrl;
import static ru.yandex.autotests.mordabackend.utils.parameters.ParametersUtils.parameters;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.matchers.collection.HasSameItemsAsCollectionMatcher.hasSameItemsAsCollection;

/**
 * User: ivannik
 * Date: 24.06.2014
 */
@Aqua.Test(title = "Topnews Stocks")
@Features("Stocks")
@Stories("Topnews Stocks")
@RunWith(CleanvarsParametrizedRunner.class)
public class TopnewsStocksTest {

    @CleanvarsParametrizedRunner.Parameters("{3}, {4}, {5}")
    public static ParametersUtils parameters =
            parameters(STOCKS_REGIONS_ALL)
                    .withLanguages(Language.RU, Language.UK, Language.BE)
                    .withUserAgents(FF_34)
                    .withCleanvarsBlocks(CleanvarsBlock.STOCKS, CleanvarsBlock.TOPNEWS, CleanvarsBlock.BLOCKS);

    private final Client client;
    private Region region;
    private Language language;
    private UserAgent userAgent;
    private Cleanvars cleanvars;
    private StocksFlatEntry stocksFlatEntry;

    public TopnewsStocksTest(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                             Language language, UserAgent userAgent) {
        this.region = region;
        this.language = language;
        this.client = client;
        this.userAgent = userAgent;
        this.cleanvars = cleanvars;
    }

    @Before
    public void init(){
        stocksFlatEntry = getStocksFlatEntry(region, userAgent);
        assumeFalse("Нет блока в новостях", stocksFlatEntry == null);
    }

    @Test
    public void topnewsStocksItemsCount() {
        List<String> expectedStockIds =
                extract(getTopnewsStockEntries(stocksFlatEntry), on(StocksEntry.class).getId());
        List<String> actualStockIds =
                extract(cleanvars.getTopnews().getTopnewsStocks(), on(TopnewsStocksItem.class).getId());

        shouldMatchTo(actualStockIds, hasSameItemsAsCollection(expectedStockIds));
    }

    @Test
    public void topnewsStocksItemFields() {
        Map<String, TopnewsStocksItem> items =
                index(cleanvars.getTopnews().getTopnewsStocks(), on(TopnewsStocksItem.class).getId());
        for (StocksEntry stocksEntry : getTopnewsStockEntries(stocksFlatEntry)) {
            shouldHaveParameter(items.get(stocksEntry.getId()),
                    having(on(TopnewsStocksItem.class).getText(), anyOf(
                            equalTo(getTranslation(
                                    "home",
                                    "rates",
                                    "stocks." + stocksEntry.getId() + ".short", language)),
                            equalTo(getTranslation(
                                    "home",
                                    "rates",
                                    "stocks." + stocksEntry.getId() + ".text", language)
                                    .replaceAll("(?<=(USD|EUR|RUB)).", " ")),
                            equalTo("Нефть")

                    )));
            if (region.getDomain().equals(Domain.RU) || region.getDomain().equals(Domain.KZ)) {
                shouldHaveParameter(items.get(stocksEntry.getId()),
                        having(on(TopnewsStocksItem.class).getAlt(), startsWith(getTranslation("home", "rates",
                                "stocks." + stocksEntry.getId() + ".source", language))));
            }
            shouldHaveParameter(items.get(stocksEntry.getId()),
                    having(on(TopnewsStocksItem.class).getValue(), VALUE_SHORT_MATCHER));
        }
    }

    @Test
    public void topnewsStocksItemFHref() throws IOException {

        for (TopnewsStocksItem item : cleanvars.getTopnews().getTopnewsStocks()) {
            String url = normalizeUrl(item.getHref());
            addLink(url, region, false, language, userAgent);
            shouldHaveResponseCode(client, url, userAgent, lessThan(400));
        }
    }
}
