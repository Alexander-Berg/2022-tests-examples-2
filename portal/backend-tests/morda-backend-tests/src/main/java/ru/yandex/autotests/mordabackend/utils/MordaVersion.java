package ru.yandex.autotests.mordabackend.utils;

import ru.yandex.autotests.mordaexportsclient.MordaExports;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.autotests.utils.morda.BaseProperties;

import static ru.yandex.autotests.mordaexportsclient.MordaExports.SERVICES_V12_2;

/**
 * User: ivannik
 * Date: 11.06.2014
 */
public enum MordaVersion {
    V12("v12", SERVICES_V12_2);

    private String name;
    private MordaExports.MordaExport<ServicesV122Entry> export;

    private MordaVersion(String name, MordaExports.MordaExport<ServicesV122Entry> export) {
        this.name = name;
        this.export = export;
    }

    public String getName() {
        return name;
    }

    public MordaExports.MordaExport<ServicesV122Entry> getExport() {
        return export;
    }

    public static MordaVersion fromMordaEnv(BaseProperties.MordaEnv mordaEnv) {
        if (mordaEnv.getEnv().contains("www")) {
            return V12;
        }
        throw new IllegalArgumentException("May not valid MordaEnv: " + mordaEnv.getEnv());
    }
}
