package ru.yandex.autotests.metrika.data.management.v1.yclidconversion;

import ru.yandex.autotests.metrika.utils.CsvField;

import java.math.BigDecimal;
import java.math.BigInteger;

public class YclidConversionUploadingData {

    public static final String COLUMN_YCLID = "Yclid";
    public static final String COLUMN_TARGET = "Target";
    public static final String COLUMN_DATE_TIME = "DateTime";
    public static final String COLUMN_PRICE = "Price";
    public static final String COLUMN_CURRENCY = "Currency";

    @CsvField(COLUMN_YCLID)
    private String yclid;

    @CsvField(COLUMN_TARGET)
    private String target;

    @CsvField(COLUMN_DATE_TIME)
    private Long dateTime;

    @CsvField(COLUMN_PRICE)
    private String price;

    @CsvField(COLUMN_CURRENCY)
    private String currency;

    public String getYclid() {
        return yclid;
    }

    public void setYclid(String yclid) {
        this.yclid = yclid;
    }

    public String getTarget() {
        return target;
    }

    public void setTarget(String target) {
        this.target = target;
    }

    public Long getDateTime() {
        return dateTime;
    }

    public void setDateTime(Long dateTime) {
        this.dateTime = dateTime;
    }

    public String getPrice() {
        return price;
    }

    public void setPrice(String price) {
        this.price = price;
    }

    public String getCurrency() {
        return currency;
    }

    public void setCurrency(String currency) {
        this.currency = currency;
    }
    
   public YclidConversionUploadingData withYclid(String yclid) {
        this.yclid = yclid;
        return this;
    }

    public YclidConversionUploadingData withTarget(String target) {
        this.target = target;
        return this;
    }

    public YclidConversionUploadingData withDateTime(Long dateTime) {
        this.dateTime = dateTime;
        return this;
    }

    public YclidConversionUploadingData withPrice(String price) {
        this.price = price;
        return this;
    }

    public YclidConversionUploadingData withCurrency(String currency) {
        this.currency = currency;
        return this;
    }
    
}
