package ru.yandex.metrika.userparams.sharder.config;

public class UserParamsSharderSettings {

    private static final String userparamsUpdatesTopic = "userparams-sharded-log";
    private static final String userparamsSharderSourceId = "userparams-sharder";
    private static final String userapramsTopic = "userparams-log";
    private static final String userparamsConsumer = "userparams-consumer";
    private static final String userparamsPoolName = "userparams-sharder";


    public static String getUserparamsUpdatesTopic() {
        return userparamsUpdatesTopic;
    }

    public static String getUserparamsSharderSourceId() {
        return userparamsSharderSourceId;
    }

    public static String getUserapramsTopic() {
        return userapramsTopic;
    }

    public static String getUserparamsConsumer() {
        return userparamsConsumer;
    }

    public static String getUserparamsPoolName() {
        return userparamsPoolName;
    }
}
