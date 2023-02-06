package ru.yandex.autotests.morda.monitorings.poi.searchapi;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.api.search.SearchApiBlock;
import ru.yandex.autotests.morda.beans.api.search.v1.poi.PoiApiV1;
import ru.yandex.autotests.morda.beans.api.search.v1.poi.PoiApiV1Group;
import ru.yandex.autotests.morda.monitorings.BaseSearchApiMonitoring;
import ru.yandex.autotests.morda.pages.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.main.MainMorda;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.util.stream.Collectors.toList;
import static ru.yandex.autotests.morda.api.search.SearchApiBlock.POI;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.tests.searchapi.MordaSearchapiTestsProperties.POI_REGIONS;

/**
 * User: asamar
 * Date: 27.06.16
 */
@Aqua.Test(title = "Poi search api monitoring")
@Features({"Search-api", "Poi"})
@RunWith(Parameterized.class)
public class PoiSearchApiMonitoring extends BaseSearchApiMonitoring<PoiApiV1> {

    private PoiApiV1 poi;

    public PoiSearchApiMonitoring(MainMorda<?> morda) {
        super(morda);

    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<DesktopMainMorda> data() {
        List<DesktopMainMorda> data = new ArrayList<>();
        POI_REGIONS.forEach(region -> data.add(desktopMain().region(region)));

        return data;
    }

    @Override
    protected PoiApiV1 getSearchApiBlock() {
        MordaClient mordaClient = new MordaClient();

        poi = mordaClient.search().v1(CONFIG.getEnvironment(), SearchApiBlock.POI)
                .withGeo(morda.getRegion())
                .read()
                .getPoi();

        return poi;
    }

    @Override
    protected SearchApiBlock getSearchApiBlockName() {
        return POI;
    }

    @Override
    protected List<String> getSearchApiNames() {
        List<String> names = new ArrayList<>();

        names.addAll(poi.getData().getGroups().stream()
                .map(PoiApiV1Group::getTitle)
                .collect(toList()));

        return names;
    }

    @Override
    protected List<String> getSearchApiUrls() {
        List<String> urls = new ArrayList<>();

        urls.addAll(poi.getData().getGroups().stream()
                .map(PoiApiV1Group::getIcon)
                .collect(toList()));

        urls.add(poi.getData().getMapUrl());

        return urls;
    }
}
