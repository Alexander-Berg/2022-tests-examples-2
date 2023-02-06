package ru.yandex.autotests.morda.monitorings.topnews.searchapi;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.api.search.SearchApiBlock;
import ru.yandex.autotests.morda.beans.api.search.v1.topnews.TopnewsApiV1;
import ru.yandex.autotests.morda.beans.api.search.v1.topnews.TopnewsApiV1Item;
import ru.yandex.autotests.morda.beans.api.search.v1.topnews.TopnewsApiV1Tab;
import ru.yandex.autotests.morda.monitorings.BaseSearchApiMonitoring;
import ru.yandex.autotests.morda.pages.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.main.MainMorda;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.util.stream.Collectors.toList;
import static ru.yandex.autotests.morda.api.search.SearchApiBlock.TOPNEWS;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.tests.searchapi.MordaSearchapiTestsProperties.TOPNEWS_REGIONS;

/**
 * User: asamar
 * Date: 27.06.16
 */
@Aqua.Test(title = "Topnews search api monitoring")
@Features({"Search-api", "Topnews"})
@RunWith(Parameterized.class)
public class TopnewsSearchApiMonitoring extends BaseSearchApiMonitoring<TopnewsApiV1> {
    private TopnewsApiV1 topnews;

    public TopnewsSearchApiMonitoring(MainMorda<?> morda) {
        super(morda);

    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<DesktopMainMorda> data() {
        List<DesktopMainMorda> data = new ArrayList<>();
        TOPNEWS_REGIONS.forEach(region -> data.add(desktopMain().region(region)));

        return data;
    }

    @Override
    protected TopnewsApiV1 getSearchApiBlock() {
        MordaClient mordaClient = new MordaClient();

        topnews = mordaClient.search().v1(CONFIG.getEnvironment(), SearchApiBlock.TOPNEWS)
                .withGeo(morda.getRegion())
                .read()
                .getTopnews();

        return topnews;
    }

    @Override
    protected SearchApiBlock getSearchApiBlockName() {
        return TOPNEWS;
    }

    @Override
    protected List<String> getSearchApiNames() {
        List<String> names = new ArrayList<>();

        topnews.getData().getTab().stream()
                .peek(tab -> names.add(tab.getTitle()))
                .flatMap(e -> e.getNews().stream())
                .forEach(news -> names.add(news.getText()));

        return names;
    }

    @Override
    protected List<String> getSearchApiUrls() {
        List<String> urls;

        urls = topnews.getData()
                .getTab().stream()
                .flatMap(e -> e.getNews().stream())
                .map(TopnewsApiV1Item::getUrl)
                .collect(toList());

        urls.addAll(topnews.getData()
                .getTab().stream()
                .map(TopnewsApiV1Tab::getUrl)
                .collect(toList()));

        urls.add(topnews.getData().getUrl());

        return urls;
    }
}
