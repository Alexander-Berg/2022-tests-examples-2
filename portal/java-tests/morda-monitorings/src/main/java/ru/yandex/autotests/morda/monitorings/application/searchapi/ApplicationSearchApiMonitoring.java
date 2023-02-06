package ru.yandex.autotests.morda.monitorings.application.searchapi;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.MordaClient;
import ru.yandex.autotests.morda.api.search.SearchApiBlock;
import ru.yandex.autotests.morda.beans.api.search.v1.application.ApplicationApiV1;
import ru.yandex.autotests.morda.beans.api.search.v1.application.ApplicationApiV1Item;
import ru.yandex.autotests.morda.monitorings.BaseSearchApiMonitoring;
import ru.yandex.autotests.morda.pages.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.main.MainMorda;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.util.stream.Collectors.toList;
import static ru.yandex.autotests.morda.api.search.SearchApiBlock.APPLICATION;
import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.tests.searchapi.MordaSearchapiTestsProperties.APPLICATION_REGIONS;

/**
 * User: asamar
 * Date: 27.06.16
 */
@Aqua.Test(title = "Application search api monitoring")
@Features({"Search-api", "Application"})
@RunWith(Parameterized.class)
public class ApplicationSearchApiMonitoring extends BaseSearchApiMonitoring<ApplicationApiV1> {

    private ApplicationApiV1 apps;

    public ApplicationSearchApiMonitoring(MainMorda<?> morda) {
        super(morda);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<DesktopMainMorda> data() {
        List<DesktopMainMorda> data = new ArrayList<>();
        APPLICATION_REGIONS.stream().forEach(region -> data.add(desktopMain().region(region)));

        return data;
    }

    @Override
    protected ApplicationApiV1 getSearchApiBlock() {
        MordaClient mordaClient = new MordaClient();
        apps = mordaClient.search()
                .v1(CONFIG.getEnvironment(), SearchApiBlock.APPLICATION)
                .withGeo(morda.getRegion())
                .read()
                .getApplication();

        return apps;
    }

    @Override
    protected SearchApiBlock getSearchApiBlockName() {
        return APPLICATION;
    }

    @Override
    protected List<String> getSearchApiNames() {
        List<String> names = new ArrayList<>();
        apps.getData().getList().stream().forEach(e -> {
                    names.add(e.getId());
                    names.add(e.getTitle());
                }
        );
        return names;
    }

    @Override
    protected List<String> getSearchApiUrls() {
        List<String> urls = new ArrayList<>();

        urls.addAll(apps.getData().getList().stream()
                .map(ApplicationApiV1Item::getUrl)
                .collect(toList()));

        urls.addAll(apps.getData().getList().stream()
                .map(ApplicationApiV1Item::getIcon)
                .collect(toList()));

        return urls;
    }
}
