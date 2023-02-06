package ru.yandex.autotests.metrika.data.management.v1.offlineconversion;

import java.math.BigInteger;

import ru.yandex.autotests.metrika.utils.CsvField;

/**
 * @author zgmnkv
 */
public class CallsOfflineConversionUploadingData extends OfflineConversionUploadingData {

    public static final String COLUMN_PHONE_NUMBER = "PhoneNumber";
    public static final String COLUMN_TALK_DURATION = "TalkDuration";
    public static final String COLUMN_HOLD_DURATION = "HoldDuration";
    public static final String COLUMN_CALL_MISSED = "CallMissed";
    public static final String COLUMN_TAG = "Tag";
    public static final String COLUMN_FIRST_TIME_CALLER = "FirstTimeCaller";
    public static final String COLUMN_URL = "URL";
    public static final String COLUMN_CALL_TRACKER_URL = "CallTrackerURL";
    public static final String COLUMN_STATIC_CALL = "StaticCall";

    @CsvField(COLUMN_PHONE_NUMBER)
    private String phoneNumber;

    @CsvField(COLUMN_TALK_DURATION)
    private Long talkDuration;

    @CsvField(COLUMN_HOLD_DURATION)
    private Long holdDuration;

    @CsvField(COLUMN_CALL_MISSED)
    private Integer callMissed;

    @CsvField(COLUMN_TAG)
    private String tag;

    @CsvField(COLUMN_FIRST_TIME_CALLER)
    private Integer firstTimeCaller;

    @CsvField(COLUMN_URL)
    private String url;

    @CsvField(COLUMN_CALL_TRACKER_URL)
    private String callTrackerUrl;

    @CsvField(COLUMN_STATIC_CALL)
    private Integer staticCall;

    @Override
    public CallsOfflineConversionUploadingData withUserId(String userId) {
        return (CallsOfflineConversionUploadingData) super.withUserId(userId);
    }

    @Override
    public CallsOfflineConversionUploadingData withClientId(BigInteger clientId) {
        return (CallsOfflineConversionUploadingData) super.withClientId(clientId);
    }

    @Override
    public CallsOfflineConversionUploadingData withYclid(BigInteger yclid) {
        return (CallsOfflineConversionUploadingData) super.withYclid(yclid);
    }

    @Override
    public CallsOfflineConversionUploadingData withDateTime(Long dateTime) {
        return (CallsOfflineConversionUploadingData) super.withDateTime(dateTime);
    }

    @Override
    public CallsOfflineConversionUploadingData withPrice(String price) {
        return (CallsOfflineConversionUploadingData) super.withPrice(price);
    }

    @Override
    public CallsOfflineConversionUploadingData withCurrency(String currency) {
        return (CallsOfflineConversionUploadingData) super.withCurrency(currency);
    }

    public String getPhoneNumber() {
        return phoneNumber;
    }

    public void setPhoneNumber(String phoneNumber) {
        this.phoneNumber = phoneNumber;
    }

    public CallsOfflineConversionUploadingData withPhoneNumber(String phoneNumber) {
        this.phoneNumber = phoneNumber;
        return this;
    }

    public Long getTalkDuration() {
        return talkDuration;
    }

    public void setTalkDuration(Long talkDuration) {
        this.talkDuration = talkDuration;
    }

    public CallsOfflineConversionUploadingData withTalkDuration(Long talkDuration) {
        this.talkDuration = talkDuration;
        return this;
    }

    public Long getHoldDuration() {
        return holdDuration;
    }

    public void setHoldDuration(Long holdDuration) {
        this.holdDuration = holdDuration;
    }

    public CallsOfflineConversionUploadingData withHoldDuration(Long holdDuration) {
        this.holdDuration = holdDuration;
        return this;
    }

    public Integer getCallMissed() {
        return callMissed;
    }

    public void setCallMissed(Integer callMissed) {
        this.callMissed = callMissed;
    }

    public CallsOfflineConversionUploadingData withCallMissed(Integer callMissed) {
        this.callMissed = callMissed;
        return this;
    }

    public String getTag() {
        return tag;
    }

    public void setTag(String tag) {
        this.tag = tag;
    }

    public CallsOfflineConversionUploadingData withTag(String tag) {
        this.tag = tag;
        return this;
    }

    public Integer getFirstTimeCaller() {
        return firstTimeCaller;
    }

    public void setFirstTimeCaller(Integer firstTimeCaller) {
        this.firstTimeCaller = firstTimeCaller;
    }

    public CallsOfflineConversionUploadingData withFirstTimeCaller(Integer firstTimeCaller) {
        this.firstTimeCaller = firstTimeCaller;
        return this;
    }

    public String getUrl() {
        return url;
    }

    public void setUrl(String url) {
        this.url = url;
    }

    public CallsOfflineConversionUploadingData withUrl(String url) {
        this.url = url;
        return this;
    }

    public String getCallTrackerUrl() {
        return callTrackerUrl;
    }

    public void setCallTrackerUrl(String callTrackerUrl) {
        this.callTrackerUrl = callTrackerUrl;
    }

    public CallsOfflineConversionUploadingData withCallTrackerUrl(String callTrackerUrl) {
        this.callTrackerUrl = callTrackerUrl;
        return this;
    }

    public Integer getStaticCall() {
        return staticCall;
    }

    public void setStaticCall(Integer staticCall) {
        this.staticCall = staticCall;
    }

    public CallsOfflineConversionUploadingData withStaticCall(Integer staticCall) {
        this.staticCall = staticCall;
        return this;
    }
}
