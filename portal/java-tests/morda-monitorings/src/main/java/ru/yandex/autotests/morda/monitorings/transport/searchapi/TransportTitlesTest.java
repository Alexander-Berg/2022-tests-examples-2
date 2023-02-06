package ru.yandex.autotests.morda.monitorings.transport.searchapi;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.api.search.SearchApiBlock;
import ru.yandex.autotests.morda.beans.api.search.v1.transport.TransportApiV1;
import ru.yandex.autotests.morda.beans.api.search.v1.transport.TransportApiV1Item;
import ru.yandex.autotests.morda.monitorings.BaseSearchApiMonitoring;
import ru.yandex.autotests.morda.pages.main.DesktopMainMorda;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.util.stream.Collectors.toList;
import static ru.yandex.autotests.morda.api.search.SearchApiBlock.TRANSPORT;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.tests.searchapi.MordaSearchapiTestsProperties.TRANSPORT_REGIONS;

/**
 * User: asamar
 * Date: 28.06.16
 */
@Aqua.Test(title = "Transport search api monitoring")
@Features({"Search-api", "Transport"})
@RunWith(Parameterized.class)
public class TransportTitlesTest  extends BaseSearchApiMonitoring<TransportApiV1> {
    private TransportApiV1 transport;

    public TransportTitlesTest(DesktopMainMorda morda) {
        super(morda);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<DesktopMainMorda> data() {
        List<DesktopMainMorda> data = new ArrayList<>();
        TRANSPORT_REGIONS.forEach(region -> data.add(desktopMain().region(region)));

        return data;
    }

    @Override
    protected TransportApiV1 getSearchApiBlock() {
        MordaClient mordaClient = new MordaClient();
        transport = mordaClient.search().v1(CONFIG.getEnvironment(), SearchApiBlock.TRANSPORT)
                .withGeo(morda.getRegion())
                .read()
                .getTransport();

        return transport;
    }

    @Override
    protected SearchApiBlock getSearchApiBlockName() {
        return TRANSPORT;
    }

    @Override
    protected List<String> getSearchApiNames() {
        List<String> names = new ArrayList<>();

        transport.getData().getList().forEach(e -> {
            names.add(e.getId());
            names.add(e.getTitle());
        });

        return names;
    }

    @Override
    protected List<String> getSearchApiUrls() {
        List<String> urls = new ArrayList<>();

        urls.addAll(transport.getData()
                .getList().stream()
                .map(TransportApiV1Item::getUrl)
                .filter(e -> e != null && !e.startsWith("intent"))
                .collect(toList()));

        urls.addAll(transport.getData()
                .getList().stream()
                .map(TransportApiV1Item::getIcon)
                .collect(toList()));

        return urls;
    }
}
