package ru.yandex.autotests.metrika.beans.schemes;

import org.apache.commons.csv.CSVRecord;

import java.util.ArrayList;
import java.util.List;

/**
 * Created by okunev on 19.11.2014.
 */
public class StatV1DataCsvSchema {

    private Long code;

    private List<CSVRecord> data = new ArrayList<>();

    private String message;

    private Object response;

    public Long getCode() {
        return code;
    }

    public void setCode(Long code) {
        this.code = code;
    }

    public StatV1DataCsvSchema withCode(Long code) {
        this.code = code;
        return this;
    }

    public List<CSVRecord> getData() {
        return data;
    }

    public void setData(List<CSVRecord> data) {
        this.data = data;
    }

    public StatV1DataCsvSchema withData(List<CSVRecord> data) {
        this.data = data;
        return this;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public StatV1DataCsvSchema withMessage(String message) {
        this.message = message;
        return this;
    }

    public Object getResponse() {
        return response;
    }

    public void setResponse(Object response) {
        this.response = response;
    }

    public StatV1DataCsvSchema withResponse(Object response) {
        this.response = response;
        return this;
    }

}
