package ru.yandex.metrika.userparams.sample;

import ru.yandex.metrika.userparams.Param;
import ru.yandex.metrika.userparams.ParamKey;
import ru.yandex.metrika.userparams.ParamOwner;
import ru.yandex.metrika.userparams.ParamOwnerKey;

public class SampleParamFactory {

    public static final int COUNTER_ID = 24226447;
    public static final int COUNTER_ID_2 = 24226441;

    public static final Long USER_ID = Long.parseUnsignedLong("9223372036854775808");
    public static final Long USER_ID_2 = Long.parseUnsignedLong("9223372036854775807");
    public static final Long USER_ID_3 = Long.parseUnsignedLong("123");
    public static final Long USER_ID_4 = Long.parseUnsignedLong("424242");

    public static final String PARAM_PATH = "Path_";
    public static final String PARAM_PATH_2 = "Path_2";

    public static final String VALUE_STRING = "200";
    public static final String VALUE_STRING_2 = "500";

    public static final Double VALUE_DOUBLE = 200d;
    public static final Double VALUE_DOUBLE_2 = 500d;

    public static final String CLIENT_USER_ID = "someUserId";
    public static final String CLIENT_USER_ID_2 = "anotherUserId";
    public static final String CLIENT_USER_ID_3 = "thirdUserId";

    public static final int PARAM_QUANTITY = 1;
    public static final int PARAM_QUANTITY_2 = 2;
    public static final int PARAM_QUANTITY_3 = 3;

    public static final Long VERSION_1 = 1L;

    public static Param buildSampleParam() {
        return buildParam(COUNTER_ID, USER_ID, PARAM_PATH, VALUE_STRING, VALUE_DOUBLE, VERSION_1);
    }

    public static Param buildSampleParam2() {
        return buildParam(COUNTER_ID_2, USER_ID_2, PARAM_PATH_2, VALUE_STRING_2, VALUE_DOUBLE_2, VERSION_1);
    }

    public static Param buildParam(int counterId, long userId, String paramPath, String paramValue, Double valueDouble, Long version) {
        return new Param(new ParamKey(new ParamOwnerKey(counterId, userId), paramPath), paramValue, valueDouble, version);
    }

    public static ParamOwner buildSampleParamOwner() {
        return buildParamOwner(COUNTER_ID, USER_ID, CLIENT_USER_ID, PARAM_QUANTITY);
    }

    public static ParamOwner buildSampleParamOwner2() {
        return buildParamOwner(COUNTER_ID, USER_ID_2, CLIENT_USER_ID_2, PARAM_QUANTITY_2);
    }

    public static ParamOwner buildSampleParamOwner3() {
        return buildParamOwner(COUNTER_ID, USER_ID_3, CLIENT_USER_ID_3, PARAM_QUANTITY_3);
    }

    public static ParamOwner buildSampleParamOwnerWithEmptyClientUserId() {
        return buildParamOwner(COUNTER_ID, USER_ID_4, "", PARAM_QUANTITY_2);
    }

    public static ParamOwner buildParamOwner(int counterId, Long userId, String clientUserId, int paramQuantity) {
        return new ParamOwner(new ParamOwnerKey(counterId, userId), clientUserId, paramQuantity);
    }
}
