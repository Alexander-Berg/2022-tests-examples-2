package ru.yandex.autotests.metrika.data.management.v1.offlineconversion;

import java.math.BigInteger;

import ru.yandex.autotests.metrika.utils.CsvField;

/**
 * @author zgmnkv
 */
public class OfflineConversionUploadingData {

    public static final String COLUMN_USER_ID = "UserId";
    public static final String COLUMN_CLIENT_ID = "ClientId";
    public static final String COLUMN_YCLID = "Yclid";
    public static final String COLUMN_DATE_TIME = "DateTime";
    public static final String COLUMN_PRICE = "Price";
    public static final String COLUMN_CURRENCY = "Currency";

    @CsvField(COLUMN_USER_ID)
    private String userId;

    @CsvField(COLUMN_CLIENT_ID)
    private BigInteger clientId;

    @CsvField(COLUMN_YCLID)
    private BigInteger yclid;

    @CsvField(COLUMN_DATE_TIME)
    private Long dateTime;

    @CsvField(COLUMN_PRICE)
    private String price;

    @CsvField(COLUMN_CURRENCY)
    private String currency;

    public String getUserId() {
        return userId;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }

    public OfflineConversionUploadingData withUserId(String userId) {
        this.userId = userId;
        return this;
    }

    public BigInteger getClientId() {
        return clientId;
    }

    public void setClientId(BigInteger clientId) {
        this.clientId = clientId;
    }

    public OfflineConversionUploadingData withClientId(BigInteger clientId) {
        this.clientId = clientId;
        return this;
    }

    public BigInteger getYclid() {
        return yclid;
    }

    public void setYclid(BigInteger yclid) {
        this.yclid = yclid;
    }

    public OfflineConversionUploadingData withYclid(BigInteger yclid) {
        this.yclid = yclid;
        return this;
    }

    public Long getDateTime() {
        return dateTime;
    }

    public void setDateTime(Long dateTime) {
        this.dateTime = dateTime;
    }

    public OfflineConversionUploadingData withDateTime(Long dateTime) {
        this.dateTime = dateTime;
        return this;
    }

    public String getPrice() {
        return price;
    }

    public void setPrice(String price) {
        this.price = price;
    }

    public OfflineConversionUploadingData withPrice(String price) {
        this.price = price;
        return this;
    }

    public String getCurrency() {
        return currency;
    }

    public void setCurrency(String currency) {
        this.currency = currency;
    }

    public OfflineConversionUploadingData withCurrency(String currency) {
        this.currency = currency;
        return this;
    }
}
