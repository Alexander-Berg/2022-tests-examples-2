package ru.yandex.autotests.mordabackend.beans.geo;

import com.fasterxml.jackson.annotation.JsonCreator;

/**
 * User: ivannik
 * Date: 25.07.2014
 */
public class MetaMaps {

    private int mapsInt;
    private Maps mapsObj;

    @JsonCreator
    public MetaMaps(int mapsInt) {
        this.mapsInt = mapsInt;
    }

    @JsonCreator
    public MetaMaps(String mapsString) {
        this.mapsInt = Integer.parseInt(mapsString);
    }

    @JsonCreator
    public MetaMaps(Maps mapsObj) {
        this.mapsObj = mapsObj;
    }

    public int getInt() {
        return mapsInt;
    }

    public Maps getObj() {
        return mapsObj;
    }
}
