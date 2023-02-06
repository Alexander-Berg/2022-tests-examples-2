package ru.yandex.metrika.userparams.sharder.tests;

import java.io.IOException;
import java.util.List;

import org.junit.BeforeClass;
import org.springframework.beans.factory.annotation.Autowired;

import ru.yandex.metrika.userparams.ListParamWrapper;
import ru.yandex.metrika.userparams.Param;
import ru.yandex.metrika.userparams.ParamOwnerKey;
import ru.yandex.metrika.userparams.sharder.steps.DataSteps;
import ru.yandex.metrika.userparams.sharder.steps.TestSteps;

public abstract class AbstractUserparamsSharderTest {

    @Autowired
    protected DataSteps dataSteps;

    @Autowired
    protected TestSteps testSteps;

    protected final long USER_ID_1 = 42L;
    protected final int COUNTER_ID_1 = 24;

    protected final long USER_ID_2 = 442L;
    protected final int COUNTER_ID_2 = 2;

    protected final Param PARAM_1 = new Param(new ParamOwnerKey(COUNTER_ID_1, USER_ID_1), "some.test.path", "beer", 0.);
    protected final Param PARAM_2 = new Param(new ParamOwnerKey(COUNTER_ID_1, USER_ID_1), "some.other.test.path", "12.3", 12.3);
    protected final Param PARAM_3 = new Param(new ParamOwnerKey(COUNTER_ID_1, USER_ID_1), "yet.another.path", "32.1", 32.1);

    protected final Param PARAM_4 = new Param(new ParamOwnerKey(COUNTER_ID_2, USER_ID_2), "path.was.there", "value", 0.);

    protected final String CLIENT_USER_ID = "some_client_user_id";

    protected final ListParamWrapper SINGLE_PARAM_WRAPPER = new ListParamWrapper(List.of(PARAM_1), USER_ID_1, COUNTER_ID_1, CLIENT_USER_ID);
    protected final ListParamWrapper BATCH_PARAM_WRAPPER =  new ListParamWrapper(List.of(PARAM_1, PARAM_2, PARAM_3), USER_ID_1, COUNTER_ID_1, CLIENT_USER_ID);

    protected final ListParamWrapper ANOTHER_SINGLE_PARAM_WRAPPER = new ListParamWrapper(List.of(PARAM_4), USER_ID_2, COUNTER_ID_2, CLIENT_USER_ID);

    @BeforeClass
    public static void beforeClass() throws IOException {
        UserparamsSharderTestSetup.setup();
    }

}
