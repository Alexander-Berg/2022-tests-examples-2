package ru.yandex.quasar.glagol.reporter

import com.google.gson.JsonParser
import com.yandex.metrica.IReporter
import com.yandex.metrica.Revenue
import com.yandex.metrica.ecommerce.ECommerceEvent
import com.yandex.metrica.profile.UserProfile

class SingleEventMetricaReporter : IReporter {

    private var currentParams: String? = ""
    var currentEvent: String = ""
        private set

    override fun sendEventsBuffer() {
        // unused
    }

    override fun reportEvent(s: String) {
        // unused
    }

    override fun reportEvent(p0: String, p1: String?) {
        currentEvent = p0
        currentParams = p1
    }

    override fun reportEvent(p0: String, p1: MutableMap<String, Any>?) {
        // unused
    }

    override fun reportError(s: String, throwable: Throwable?) {
        // unused
    }

    override fun reportError(p0: String, p1: String?) {
        // unused
    }

    override fun reportError(p0: String, p1: String?, p2: Throwable?) {
        // unused
    }

    override fun reportUnhandledException(p0: Throwable) {
        // unused
    }

    override fun resumeSession() {
        // unused
    }

    override fun pauseSession() {
        // unused
    }

    override fun setUserProfileID(p0: String?) {
        // unused
    }

    override fun reportUserProfile(p0: UserProfile) {
        // unused
    }

    override fun reportRevenue(p0: Revenue) {
        // unused
    }

    override fun reportECommerce(p0: ECommerceEvent) {
        // unused
    }

    override fun setStatisticsSending(p0: Boolean) {
        // unused
    }

    fun getParamsJson() =  JsonParser.parseString(currentParams).asJsonObject

}
