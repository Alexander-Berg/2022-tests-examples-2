package ru.yandex.autotests.morda.tests.bridges.searchapi;

import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.tests.AbstractTestCasesProvider;

import java.util.ArrayList;
import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.pages.MordaLanguage.BE;
import static ru.yandex.autotests.morda.pages.MordaLanguage.KK;
import static ru.yandex.autotests.morda.pages.MordaLanguage.RU;
import static ru.yandex.autotests.morda.pages.MordaLanguage.UK;
import static ru.yandex.geobase.regions.Russia.SAINT_PETERSBURG;

public class BridgesSearchApiCasesProvider extends AbstractTestCasesProvider<Object[]> {

    public BridgesSearchApiCasesProvider(String environment) {
        super(environment);
    }

    @Override
    public List<Object[]> getBaseTestCases() {
        List<Object[]> data = new ArrayList<>();
        for (MordaLanguage language : asList(RU, UK, BE, KK)) {
            data.add(new Object[]{SAINT_PETERSBURG, language});
        }
        return data;
    }

    @Override
    public List<Object[]> getSmokeTestCases() {
        return getBaseTestCases();
    }
}