package com.yandex.metrica;

import android.util.Log;

import org.json.JSONObject;

public class YandexMetrica {

    public void reportEvent(String event){
        Log.i("YandexMetrica", "Metrics Event: " + event);

    }

    public void reportEvent(String event, JSONObject obj){
        Log.i("YandexMetrica", "Metrics Event: " + event + ". Metrics obj: " + obj.toString());
    }
}
