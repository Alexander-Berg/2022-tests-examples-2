package ru.yandex.quasar.fakes

import org.json.JSONObject
import ru.yandex.quasar.core.MetricaReporter

@Suppress("MemberVisibilityCanBePrivate") // NOTE: because it is a special fake class to be used in test (with this fields)
class FakeMetricaReporter(
    var predefinedUUID: String = "-",
    var latencyPoints: ArrayList<String?> = ArrayList(),
    var latencies: ArrayList<Latency> = ArrayList(),
    var appEnvironmentValues: ArrayList<AppEnvironmentValue> = ArrayList(),
    var events: ArrayList<Event> = ArrayList(),
    var errors: ArrayList<Error> = ArrayList()
) : MetricaReporter {

    override fun createLatencyPoint(latencyPointName: String?) {
        latencyPoints.add(latencyPointName)
    }

    override fun reportLatency(latencyPointName: String?, eventName: String?, removePoint: Boolean) {
        latencies.add(Latency(latencyPointName, eventName, removePoint, null, null))
    }

    override fun reportLatency(latencyPointName: String?, eventName: String?, removePoint: Boolean, data: JSONObject) {
        latencies.add(Latency(latencyPointName, eventName, removePoint, data, null))
    }

    override fun reportLatency(
        latencyPointName: String?,
        eventName: String?,
        removePoint: Boolean,
        mapData: MutableMap<String, Any>
    ) {
        latencies.add(Latency(latencyPointName, eventName, removePoint, null, mapData))
    }

    override fun putAppEnvironmentValue(key: String?, value: String?) {
        appEnvironmentValues.add(AppEnvironmentValue(key, value))
    }

    override fun getUuid(): String {
        return predefinedUUID
    }

    override fun reportEvent(eventName: String?) {
        events.add(Event(eventName, null, null, null))
    }

    override fun reportEvent(eventName: String?, jsonData: String) {
        events.add(Event(eventName, jsonData, null, null))
    }

    override fun reportEvent(eventName: String?, mapData: MutableMap<String, Any>) {
        events.add(Event(eventName, null, mapData, null))
    }

    override fun reportEvent(eventName: String?, mapData: JSONObject) {
        events.add(Event(eventName, null, null, mapData))
    }

    override fun reportError(errorName: String?) {
        errors.add(Error(errorName, null, null, null))
    }

    override fun reportError(errorName: String?, exception: Throwable?) {
        errors.add(Error(errorName, exception, null, null))
    }

    override fun reportError(errorName: String?, value: JSONObject) {
        errors.add(Error(errorName, null, null, value))
    }

    override fun reportError(errorName: String?, mapData: MutableMap<String, Any>) {
        errors.add(Error(errorName, null, mapData, null))
    }

    data class Latency(val pointName: String?, val eventName: String?, val removePoint: Boolean, val data: JSONObject?, val mapData: MutableMap<String, Any>?)
    data class AppEnvironmentValue(val key: String?, val value: String?)
    data class Event(val name: String?, val jsonData: String?, val mapData1: MutableMap<String, Any>?, val mapData2: JSONObject?)
    data class Error(val name: String?, val exception: Throwable?, val mapData: MutableMap<String, Any>?, val jsonValue: JSONObject?)
}
