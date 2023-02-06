package ru.yandex.metrika.userparams.proto;

import java.util.List;

import org.junit.Test;

import ru.yandex.metrika.api.management.client.external.userparams.UserParamAction;
import ru.yandex.metrika.api.management.client.external.userparams.UserParamUpdate;
import ru.yandex.metrika.userparams.ListParamWrapper;
import ru.yandex.metrika.userparams.Param;
import ru.yandex.metrika.userparams.ParamOwnerKey;

import static org.junit.Assert.assertEquals;

public class UserParamsUpdateProtoSerializerTest {

    protected final long USER_ID_1 = 42L;
    protected final int COUNTER_ID_1 = 24;

    protected final Param PARAM_1 = new Param(new ParamOwnerKey(COUNTER_ID_1, USER_ID_1), "some.test.path", "beer", 0.);
    protected final Param PARAM_2 = new Param(new ParamOwnerKey(COUNTER_ID_1, USER_ID_1), "some.other.test.path", "12.3", 12.3);
    protected final Param PARAM_3 = new Param(new ParamOwnerKey(COUNTER_ID_1, USER_ID_1), "yet.another.path", "32.1", 32.1);
    protected final Param EMPTY_PARAM = new Param(new ParamOwnerKey(COUNTER_ID_1, USER_ID_1), "", "", 0.);

    protected final String CLIENT_USER_ID = "some_client_user_id";

    @Test
    public void updateTestE2E() {
        ListParamWrapper paramWrapper = new ListParamWrapper(List.of(PARAM_1, PARAM_2, PARAM_3), USER_ID_1, COUNTER_ID_1, CLIENT_USER_ID);

        var update = new UserParamUpdate(paramWrapper, UserParamAction.UPDATE);

        var serializer = new UserParamsUpdateProtoSerializer(new UserParamsProtoSerializer());

        assertEquals(update, serializer.deserialize(serializer.serialize(update)));
    }

    @Test
    public void emptyParamWithClientUserIdTest() {
        ListParamWrapper paramWrapper = new ListParamWrapper(List.of(EMPTY_PARAM), USER_ID_1, COUNTER_ID_1, CLIENT_USER_ID);

        var update = new UserParamUpdate(paramWrapper, UserParamAction.UPDATE);

        var serializer = new UserParamsUpdateProtoSerializer(new UserParamsProtoSerializer());

        assertEquals(update, serializer.deserialize(serializer.serialize(update)));
    }

    @Test
    public void deleteTestE2E() {
        ListParamWrapper paramWrapper = new ListParamWrapper(List.of(PARAM_1, PARAM_2, PARAM_3), USER_ID_1, COUNTER_ID_1, CLIENT_USER_ID);

        var update = new UserParamUpdate(paramWrapper, UserParamAction.DELETE_KEYS);

        var serializer = new UserParamsUpdateProtoSerializer(new UserParamsProtoSerializer());

        assertEquals(update, serializer.deserialize(serializer.serialize(update)));
    }
}
