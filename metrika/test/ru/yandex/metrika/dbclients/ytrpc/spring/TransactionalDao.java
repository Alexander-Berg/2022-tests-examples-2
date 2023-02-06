package ru.yandex.metrika.dbclients.ytrpc.spring;

import org.springframework.transaction.annotation.Transactional;

interface TransactionalDao {
    @Transactional("txManager")
    void daoMethod();
}
