package ru.yandex.autotests.tuneclient;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
public class TuneResponse {
    private final String status;
    private final String msg;

    public TuneResponse(
            @JsonProperty("status") String status,
            @JsonProperty("msg") String msg)
    {
        this.status = status;
        this.msg = msg;
    }

    public String getStatus() {
        return status;
    }

    public String getMsg() {
        return msg;
    }

    @Override
    public String toString() {
        return "TuneResponse{" +
                "status='" + status + '\'' +
                ", msg='" + msg + '\'' +
                '}';
    }
}
