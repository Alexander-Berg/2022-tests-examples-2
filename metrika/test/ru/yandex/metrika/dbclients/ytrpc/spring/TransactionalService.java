package ru.yandex.metrika.dbclients.ytrpc.spring;

import org.springframework.transaction.annotation.Transactional;

interface TransactionalService {
    @Transactional("txManager")
    void serviceMethod();
}
