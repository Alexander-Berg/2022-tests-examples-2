package ru.yandex.autotests.morda.monitorings.bridges.searchapi;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.api.search.SearchApiBlock;
import ru.yandex.autotests.morda.beans.api.search.v1.bridges.BridgesApiV1;
import ru.yandex.autotests.morda.beans.api.search.v1.bridges.BridgesApiV1Item;
import ru.yandex.autotests.morda.monitorings.BaseSearchApiMonitoring;
import ru.yandex.autotests.morda.pages.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.main.MainMorda;
import ru.yandex.geobase.regions.Russia;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;

import static ru.yandex.autotests.morda.api.search.SearchApiBlock.BRIDGES;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;

/**
 * User: asamar
 * Date: 24.06.16
 */
@Aqua.Test(title = "Bridges search api monitoring")
@Features({"Search-api", "Bridges"})
@RunWith(Parameterized.class)
public class BridgesSearchApiMonitoring extends BaseSearchApiMonitoring<BridgesApiV1> {

    private BridgesApiV1 bridges;

    public BridgesSearchApiMonitoring(MainMorda<?> morda) {
        super(morda);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<DesktopMainMorda> data() {
        List<DesktopMainMorda> data = new ArrayList<>();

        data.add(desktopMain()
                .region(Russia.SAINT_PETERSBURG));

        return data;
    }

    @Override
    protected BridgesApiV1 getSearchApiBlock() {
        MordaClient mordaClient = new MordaClient();
        bridges = mordaClient.search().v1(CONFIG.getEnvironment(), SearchApiBlock.BRIDGES)
                .withGeo(morda.getRegion())
                .read()
                .getBridges();
        return bridges;
    }

    @Override
    protected SearchApiBlock getSearchApiBlockName() {
        return BRIDGES;
    }

    @Override
    protected List<String> getSearchApiNames() {
        List<String> names = new ArrayList<>();

        bridges.getData().get0().stream().forEach(e -> {
            names.add(e.getBridgeName());
            names.add(e.getBridgeRaise1Dt());
            names.add(e.getBridgeLower1Dt());
        });

        bridges.getData().get1().stream().forEach(e -> {
            names.add(e.getBridgeName());
            names.add(e.getBridgeRaise1Dt());
            names.add(e.getBridgeLower1Dt());
        });

        return names;
    }

    @Override
    protected List<String> getSearchApiUrls() {
        List<String> urls = new ArrayList<>();

        urls.addAll(bridges.getData().get0().stream()
                        .map(BridgesApiV1Item::getUrl)
                        .collect(Collectors.toList())
        );
        urls.addAll(bridges.getData().get1().stream()
                        .map(BridgesApiV1Item::getUrl)
                        .collect(Collectors.toList())
        );
        return urls;
    }
}
