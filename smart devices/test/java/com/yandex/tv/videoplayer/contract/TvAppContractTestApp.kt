package com.yandex.tv.videoplayer.contract

import android.app.Application
import com.yandex.tv.live.providers.SourceInfoProvider

class TvAppContractTestApp : Application()

class TestSourceInfoProvider : SourceInfoProvider() {
    override fun getCallingPackageWrapped(): String {
        return "com.yandex.tv.test"
    }
}
