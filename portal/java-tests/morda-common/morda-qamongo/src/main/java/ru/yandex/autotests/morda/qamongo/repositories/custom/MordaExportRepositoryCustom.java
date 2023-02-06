package ru.yandex.autotests.morda.qamongo.repositories.custom;

import ru.yandex.autotests.morda.qamongo.exports.MordaExport;

import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 05/08/16
 */
public interface MordaExportRepositoryCustom {
    MordaExport get(String name, boolean stable);

    void updateStable(String name);

    void updateUnstable(String name, List<Object> data);

    default MordaExport getStable(String name) {
        return get(name, true);
    }

    default MordaExport getUnstable(String name) {
        return get(name, false);
    }
}
