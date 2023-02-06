package ru.yandex.autotests.morda.monitorings.tv.searchapi;

import org.apache.commons.lang3.RandomStringUtils;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.api.search.SearchApiBlock;
import ru.yandex.autotests.morda.beans.api.search.v1.tv.TvApiV1;
import ru.yandex.autotests.morda.beans.api.search.v1.tv.TvApiV1Program;
import ru.yandex.autotests.morda.beans.api.search.v1.tv.TvApiV1Tab;
import ru.yandex.autotests.morda.monitorings.BaseSearchApiMonitoring;
import ru.yandex.autotests.morda.pages.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.main.MainMorda;
import ru.yandex.qatools.allure.annotations.Features;

import javax.ws.rs.core.UriBuilder;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;

import static java.util.stream.Collectors.toList;
import static ru.yandex.autotests.morda.api.search.SearchApiBlock.TV;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.tests.searchapi.MordaSearchapiTestsProperties.TV_REGIONS;

/**
 * User: asamar
 * Date: 28.06.16
 */
@Aqua.Test(title = "Tv search api monitoring")
@Features({"Search-api", "TV"})
@RunWith(Parameterized.class)
public class TvSearchApiMonitoring extends BaseSearchApiMonitoring<TvApiV1> {
    private TvApiV1 tv;

    public TvSearchApiMonitoring(MainMorda<?> morda) {
        super(morda);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<DesktopMainMorda> data() {
        List<DesktopMainMorda> data = new ArrayList<>();
        TV_REGIONS.forEach(region -> data.add(desktopMain().region(region)));

        return data;
    }

    @Override
    protected TvApiV1 getSearchApiBlock() {
        MordaClient mordaClient = new MordaClient();

        tv = mordaClient.search().v1(CONFIG.getEnvironment(), SearchApiBlock.TV)
                .withGeo(morda.getRegion())
                .read()
                .getTv();

        return tv;
    }

    @Override
    protected SearchApiBlock getSearchApiBlockName() {
        return TV;
    }

    @Override
    protected List<String> getSearchApiNames() {
        List<String> names = new ArrayList<>();
        tv.getData().getTab().stream()
                .peek(tab -> {
                    names.add(tab.getTitle());
                    names.add(tab.getType());
                })
                .flatMap(e -> e.getProgram().stream())
                .filter(program -> !"separator".equals(program.getType()))
                .forEach(program -> {
                    names.add(program.getTitle());
                    names.add(program.getTime());
                    names.add(program.getProgramId());
                    names.add(program.getEventId());
                });

        return names;
    }

    @Override
    protected List<String> getSearchApiUrls() {
        List<String> urls = new ArrayList<>();

        urls.addAll(tv.getData()
                .getTab().stream()
                .map(TvApiV1Tab::getUrl)
                .collect(toList()));

        urls.addAll(tv.getData()
                .getTab().stream()
                .flatMap(e -> e.getProgram().stream())
                .filter(e -> !"separator".equals(e.getType()))
                .map(TvApiV1Program::getUrl)
                .collect(toList()));

        urls.add(tv.getData().getUrl());

        return urls.stream()
                .map(e -> UriBuilder.fromUri(e).queryParam("test_request_id",
                        RandomStringUtils.random(10, true, true) + "." + System.currentTimeMillis())
                        .build()
                        .toASCIIString()
                ).collect(Collectors.toList());
    }
}
