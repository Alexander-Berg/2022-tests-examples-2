package ru.yandex.autotests.metrika.beans.schemes;

import org.apache.poi.xssf.usermodel.XSSFSheet;

/**
 * Created by okunev on 19.11.2014.
 */
public class StatV1DataXlsxSchema {

    private Long code;

    private XSSFSheet data;

    private String message;

    private Object response;

    public Long getCode() {
        return code;
    }

    public void setCode(Long code) {
        this.code = code;
    }

    public StatV1DataXlsxSchema withCode(Long code) {
        this.code = code;
        return this;
    }

    public XSSFSheet getData() {
        return data;
    }

    public void setData(XSSFSheet data) {
        this.data = data;
    }

    public StatV1DataXlsxSchema withData(XSSFSheet data) {
        this.data = data;
        return this;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public StatV1DataXlsxSchema withMessage(String message) {
        this.message = message;
        return this;
    }

    public Object getResponse() {
        return response;
    }

    public void setResponse(Object response) {
        this.response = response;
    }

    public StatV1DataXlsxSchema withResponse(Object response) {
        this.response = response;
        return this;
    }

}
