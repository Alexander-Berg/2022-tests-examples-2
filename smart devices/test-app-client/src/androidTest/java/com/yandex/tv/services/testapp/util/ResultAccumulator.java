package com.yandex.tv.services.testapp.util;

import java.util.ArrayList;
import java.util.List;

public class ResultAccumulator {

    private final List<Float> measurements = new ArrayList<>();

    public void addMeasurement(float measurement) {
        measurements.add(measurement);
    }

    public float avg() {
        float total = 0;
        for (float m : measurements) {
            total += m;
        }
        return total / measurements.size();
    }

}
