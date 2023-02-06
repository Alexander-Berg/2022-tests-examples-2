package ru.yandex.autotests.mordabackend.utils;

import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Step;

import javax.ws.rs.client.Client;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 17.06.14
 */
public class TuneUtils {

    @Step("Set region {3}")
    public static void setRegion(MordaClient mordaClient, Client client, Region region) {
        mordaClient.tuneActions(client).setRegion(region);
    }

    @Step("Set language {3}")
    public static void setLanguage(MordaClient mordaClient, Client client, String sk, Language lang) {
        mordaClient.cleanvarsActions(client).setLanguage(lang.getExportValue(), sk);
    }
}
