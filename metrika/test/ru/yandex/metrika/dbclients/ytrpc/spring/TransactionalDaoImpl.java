package ru.yandex.metrika.dbclients.ytrpc.spring;

import org.springframework.transaction.annotation.Transactional;

class TransactionalDaoImpl implements TransactionalDao {

    private boolean fail;

    public TransactionalDaoImpl(boolean fail) {
        this.fail = fail;
    }

    @Override
    @Transactional(value = "txManager")
    public void daoMethod() {
        if (fail) throw new RuntimeException();
    }
}
