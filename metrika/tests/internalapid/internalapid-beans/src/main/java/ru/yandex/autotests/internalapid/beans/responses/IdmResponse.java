package ru.yandex.autotests.internalapid.beans.responses;

import com.fasterxml.jackson.annotation.JsonProperty;

public class IdmResponse extends InternalApidResponse {
    private Data data;
    private String warning;
    private String error;

    public Data getData() {
        return data;
    }

    public String getWarning() {
        return warning;
    }

    public String getError() {
        return error;
    }

    public static class Data {
        @JsonProperty("passport-login")
        private String passportLogin;

        @JsonProperty("counter_id")
        private int counterId;

        @JsonProperty("grant_type")
        private String grantType;

        public String getPassportLogin() {
            return passportLogin;
        }

        public int getCounterId() {
            return counterId;
        }

        public String getGrantType() {
            return grantType;
        }
    }
}
