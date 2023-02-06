package ru.yandex.autotests.morda.qamongo.repositories;

import org.springframework.data.repository.CrudRepository;
import ru.yandex.autotests.morda.qamongo.exports.MordaExport;
import ru.yandex.autotests.morda.qamongo.repositories.custom.MordaExportRepositoryCustom;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 05/08/16
 */
public interface MordaExportRepository extends CrudRepository<MordaExport, String>, MordaExportRepositoryCustom {
}
