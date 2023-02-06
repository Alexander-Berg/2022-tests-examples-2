package ru.yandex.metrika.dbclients.ytrpc.spring;

import org.springframework.transaction.annotation.Transactional;

class TransactionalServiceImpl implements TransactionalService {
    private final TransactionalDao transactionalDao;

    public TransactionalServiceImpl(TransactionalDao transactionalDao) {
        this.transactionalDao = transactionalDao;
    }

    @Override
    @Transactional("txManager")
    public void serviceMethod() {
        transactionalDao.daoMethod();
    }
}
