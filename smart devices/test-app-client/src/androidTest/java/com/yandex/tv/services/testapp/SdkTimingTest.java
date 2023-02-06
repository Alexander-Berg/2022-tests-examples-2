package com.yandex.tv.services.testapp;

import android.content.Context;
import android.util.Log;

import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;

import com.yandex.tv.services.testapp.util.ResultAccumulator;

import org.junit.Test;
import org.junit.runner.RunWith;

import java.util.concurrent.TimeUnit;

@RunWith(AndroidJUnit4.class)
public class SdkTimingTest {

    private static final String TAG = "SdkTimingTest";

    @Test
    public void measureTrivialRequestTimes() throws Exception {
        Context context = InstrumentationRegistry.getInstrumentation().getTargetContext();

        TestServiceSdk2 sdk = TestServiceSdk2.Factory.create(context, "com.yandex.tv.services.testapp");
        ResultAccumulator accumulator;
        int cycleCount = 100;

        // preheat. first request is always significantly longer because
        // 1) waiting for service to bind
        // 2) service has initialization stuff
        accumulator = new ResultAccumulator();
        measureTrivialRequestFullTime(sdk, accumulator);
        Log.d(TAG, String.format("first-request: %.2fms", accumulator.avg()));

        accumulator = new ResultAccumulator();
        for (int i = 0; i < cycleCount; i++) {
            measureTrivialRequestFullTime(sdk, accumulator);
        }
        Log.d(TAG, String.format("await-result avg: %.2fms", accumulator.avg()));

        accumulator = new ResultAccumulator();
        for (int i = 0; i < cycleCount; i++) {
            measureTrivialRequestOneWayTime(sdk, accumulator);
        }
        Log.d(TAG, String.format("one-way avg: %.2fms", accumulator.avg()));
    }

    private void measureTrivialRequestFullTime(TestServiceSdk2 sdk, ResultAccumulator accumulator) throws Exception {
        long startTime = System.nanoTime();
        String response = sdk.getConstantString().get(5000, TimeUnit.MILLISECONDS);
        long endTime = System.nanoTime();
        float duration = (endTime - startTime) / 1000000f;
        accumulator.addMeasurement(duration);
//        Log.d(TAG, String.format("await-result time: %.2fms", (endTime - startTime) / 1000000f));
    }

    private void measureTrivialRequestOneWayTime(TestServiceSdk2 sdk, ResultAccumulator accumulator) {
        long startTime = System.nanoTime();
        sdk.getConstantString();
        long endTime = System.nanoTime();
		float duration = (endTime - startTime) / 1000000f;
		accumulator.addMeasurement(duration);
//		Log.d(TAG, String.format("one-way time: %.2fms", duration));
	}

}
