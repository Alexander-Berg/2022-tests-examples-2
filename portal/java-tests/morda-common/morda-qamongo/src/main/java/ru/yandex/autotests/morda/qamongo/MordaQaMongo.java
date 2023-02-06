package ru.yandex.autotests.morda.qamongo;

import org.springframework.context.ApplicationContext;
import org.springframework.context.support.ClassPathXmlApplicationContext;
import org.springframework.data.mongodb.core.MongoOperations;
import ru.yandex.autotests.morda.qamongo.repositories.MordaExportRepository;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 05/08/16
 */
public class MordaQaMongo {
    private static final ApplicationContext APPLICATION_CONTEXT =
            new ClassPathXmlApplicationContext("classpath*:qamongo-db-context.xml");

    public static final MongoOperations MONGO_OPERATIONS =
            (MongoOperations) APPLICATION_CONTEXT.getBean("mongoOperations");

    public static final MordaExportRepository MORDA_EXPORT_REPOSITORY =
            (MordaExportRepository) APPLICATION_CONTEXT.getBean("mordaExportRepository");
}
