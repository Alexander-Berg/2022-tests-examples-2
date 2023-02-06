package ru.yandex.autotests.metrika.data.management.v1.offlineconversion;

import java.math.BigInteger;

import ru.yandex.autotests.metrika.utils.CsvField;

/**
 * @author zgmnkv
 */
public class BasicOfflineConversionUploadingData extends OfflineConversionUploadingData {

    public static final String COLUMN_TARGET = "Target";

    @CsvField(COLUMN_TARGET)
    private String target;

    @Override
    public BasicOfflineConversionUploadingData withUserId(String userId) {
        return (BasicOfflineConversionUploadingData) super.withUserId(userId);
    }

    @Override
    public BasicOfflineConversionUploadingData withClientId(BigInteger clientId) {
        return (BasicOfflineConversionUploadingData) super.withClientId(clientId);
    }

    @Override
    public BasicOfflineConversionUploadingData withYclid(BigInteger yclid) {
        return (BasicOfflineConversionUploadingData) super.withYclid(yclid);
    }

    @Override
    public BasicOfflineConversionUploadingData withDateTime(Long dateTime) {
        return (BasicOfflineConversionUploadingData) super.withDateTime(dateTime);
    }

    @Override
    public BasicOfflineConversionUploadingData withPrice(String price) {
        return (BasicOfflineConversionUploadingData) super.withPrice(price);
    }

    @Override
    public BasicOfflineConversionUploadingData withCurrency(String currency) {
        return (BasicOfflineConversionUploadingData) super.withCurrency(currency);
    }

    public String getTarget() {
        return target;
    }

    public void setTarget(String target) {
        this.target = target;
    }

    public BasicOfflineConversionUploadingData withTarget(String target) {
        this.target = target;
        return this;
    }
}
