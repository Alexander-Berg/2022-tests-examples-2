/*
 * (C) Copyright 2021 Yandex, LLC. All rights reserved.
 */

package ru.yandex.quasar.glagol.reporter

import com.yandex.metrica.IReporter
import com.yandex.metrica.Revenue
import com.yandex.metrica.ecommerce.ECommerceEvent
import com.yandex.metrica.profile.UserProfile

class MockIReporter : IReporter {

    val args = ArrayList<Any?>()

    override fun sendEventsBuffer() {
        args.add("sendEventsBuffer")
    }

    override fun reportEvent(p0: String) {
        args.add("reportEvent")
        args.add(p0)
    }

    override fun reportEvent(p0: String, p1: String?) {
        args.add("reportEvent")
        args.add(p0)
        args.add(p1)
    }

    override fun reportEvent(p0: String, p1: MutableMap<String, Any>?) {
        args.add("reportEvent")
        args.add(p0)
        args.add(p1)
    }

    override fun reportError(p0: String, p1: Throwable?) {
        args.add("reportEvent")
        args.add(p0)
        args.add(p1)
    }

    override fun reportError(p0: String, p1: String?) {
        args.add("reportError")
        args.add(p0)
        args.add(p1)
    }

    override fun reportError(p0: String, p1: String?, p2: Throwable?) {
        args.add("reportError")
        args.add(p0)
        args.add(p1)
    }

    override fun reportUnhandledException(p0: Throwable) {
        args.add("reportEx")
        args.add(p0)
    }

    override fun resumeSession() {
        args.add("resumeSession")
    }

    override fun pauseSession() {
        args.add("pauseSession")
    }

    override fun setUserProfileID(p0: String?) {
        args.add("setUserProfile")
        args.add(p0)
    }

    override fun reportUserProfile(p0: UserProfile) {
        args.add("reportUserProfile")
        args.add(p0)
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
}
