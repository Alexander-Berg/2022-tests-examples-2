package ru.yandex.autotests.morda.monitorings.stocks.searchapi;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.api.search.SearchApiBlock;
import ru.yandex.autotests.morda.beans.api.search.v1.stocks.StocksApiV1;
import ru.yandex.autotests.morda.beans.api.search.v1.stocks.StocksApiV1Group;
import ru.yandex.autotests.morda.beans.api.search.v1.stocks.StocksApiV1Row;
import ru.yandex.autotests.morda.monitorings.BaseSearchApiMonitoring;
import ru.yandex.autotests.morda.pages.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.main.MainMorda;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.api.search.SearchApiBlock.STOCKS;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;
import static ru.yandex.geobase.regions.Belarus.MINSK;
import static ru.yandex.geobase.regions.Russia.DUBNA;
import static ru.yandex.geobase.regions.Russia.KAZAN;
import static ru.yandex.geobase.regions.Russia.MOSCOW;
import static ru.yandex.geobase.regions.Russia.NIZHNY_NOVGOROD;
import static ru.yandex.geobase.regions.Russia.NOVOSIBIRSK;
import static ru.yandex.geobase.regions.Russia.OMSK;
import static ru.yandex.geobase.regions.Russia.SAINT_PETERSBURG;
import static ru.yandex.geobase.regions.Russia.SAMARA;
import static ru.yandex.geobase.regions.Russia.VLADIVOSTOK;
import static ru.yandex.geobase.regions.Russia.VORONEZH;
import static ru.yandex.geobase.regions.Russia.YEKATERINBURG;
import static ru.yandex.geobase.regions.Ukraine.KHARKIV;
import static ru.yandex.geobase.regions.Ukraine.KYIV;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 06/06/16
 */
@Aqua.Test(title = "Stocks search api monitoring")
@Features({"Search-api", "Stocks"})
@RunWith(Parameterized.class)
public class StocksSearchApiMonitoring extends BaseSearchApiMonitoring<StocksApiV1> {
    private StocksApiV1 stocks;

    public StocksSearchApiMonitoring(MainMorda<?> morda) {
        super(morda);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<DesktopMainMorda> data() {
        List<DesktopMainMorda> data = new ArrayList<>();
        asList(MOSCOW, SAINT_PETERSBURG, NOVOSIBIRSK, VLADIVOSTOK, YEKATERINBURG,
                DUBNA, VORONEZH, OMSK, KAZAN, NIZHNY_NOVGOROD, SAMARA, KYIV, KHARKIV,
                MINSK)
                .forEach(region -> data.add(desktopMain().region(region)));

        return data;
    }

    @Override
    protected StocksApiV1 getSearchApiBlock() {
        MordaClient mordaClient = new MordaClient();

        stocks = mordaClient.search().v1(CONFIG.getEnvironment(), SearchApiBlock.STOCKS)
                .withGeo(morda.getRegion())
                .read()
                .getStocks();

        return stocks;
    }

    @Override
    protected SearchApiBlock getSearchApiBlockName() {
        return STOCKS;
    }

    @Override
    protected List<String> getSearchApiNames() {
        List<String> names = new ArrayList<>();

        stocks.getData().getGroups().stream()
                .map(StocksApiV1Group::getRows)
                .flatMap(Collection::stream)
                .forEach(row -> {
                    names.add(row.getT());
                    names.add(row.getV1());
                });

       stocks.getData().getGroups().stream()
                .filter(e -> !"cash".equals(e.getType()))
                .map(StocksApiV1Group::getRows)
                .flatMap(Collection::stream)
                .filter(row -> row.getV2() != null && !row.getV2().isEmpty())
                .forEach(row -> names.add(row.getD()));

        return names;
    }


    @Override
    protected List<String> getSearchApiUrls() {
        return stocks.getData().getGroups().stream()
                .map(StocksApiV1Group::getRows)
                .flatMap(Collection::stream)
                .map(StocksApiV1Row::getUrl)
                .filter(e -> e != null && !e.isEmpty())
                .collect(Collectors.toList());
    }
}
