package ru.yandex.autotests.morda.qamongo.repositories.custom.impl;

import com.mongodb.WriteResult;
import org.apache.log4j.Logger;
import ru.yandex.autotests.morda.qamongo.exports.MordaExport;
import ru.yandex.autotests.morda.qamongo.repositories.custom.MordaExportRepositoryCustom;

import java.util.List;

import static org.springframework.data.mongodb.core.query.Criteria.where;
import static org.springframework.data.mongodb.core.query.Query.query;
import static org.springframework.data.mongodb.core.query.Update.update;
import static ru.yandex.autotests.morda.qamongo.MordaQaMongo.MONGO_OPERATIONS;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 05/08/16
 */
public class MordaExportRepositoryCustomImpl implements MordaExportRepositoryCustom {
    private static final Logger LOGGER = Logger.getLogger(MordaExportRepositoryCustom.class);

    @Override
    public MordaExport get(String name, boolean stable) {
        LOGGER.info("Getting export \"" + name + "\" with stable=" + stable);
        MordaExport export = MONGO_OPERATIONS.findOne(
                query(where("name").is(name)).addCriteria(where("stable").is(stable)),
                MordaExport.class
        );
        if (export == null) {
            LOGGER.warn("Export \"" + name + "\" not found in stable=" + stable);
        }
        return export;
    }

    @Override
    public void updateStable(String name) {
        LOGGER.info("Updating stable export \"" + name + "\"");

        MordaExport unstable = MONGO_OPERATIONS.findOne(
                query(where("name").is(name)).addCriteria(where("stable").is(false)),
                MordaExport.class
        );

        if (unstable == null) {
            LOGGER.warn("Unstable export \"" + name + "\" not found");
            return;
        }

        WriteResult result = MONGO_OPERATIONS.upsert(
                query(where("name").is(name)).addCriteria(where("stable").is(true)),
                update("name", name).set("data", unstable.getData()).set("stable", true),
                MordaExport.class
        );
        LOGGER.info("Update result: " + result);
    }

    @Override
    public void updateUnstable(String name, List<Object> data) {
        LOGGER.info("Updating unstable export \"" + name + "\"");

        WriteResult result = MONGO_OPERATIONS.upsert(
                query(where("name").is(name)).addCriteria(where("stable").is(false)),
                update("name", name).set("data", data).set("stable", false),
                MordaExport.class
        );

        LOGGER.info("Update result: " + result);
    }

}
