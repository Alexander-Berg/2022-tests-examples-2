package ru.yandex.quasar.fakes

import ru.yandex.quasar.app.webview.WebViewWrapper
import ru.yandex.quasar.app.webview.mordovia.MordoviaLoginErrorListener
import ru.yandex.quasar.app.webview.yabro.YabroViewProvider

class FakeYabroViewProvider: YabroViewProvider {

    private var webViewWrapper: FakeWebViewWrapper? = null

    override fun getCurrent(): WebViewWrapper? {
        return webViewWrapper
    }

    override fun get(yabroClass: Int, mordoviaLoginErrorListener: MordoviaLoginErrorListener): WebViewWrapper {
        val currentYabroViewWrapper = webViewWrapper
        if (currentYabroViewWrapper!= null && currentYabroViewWrapper.yabroClass == yabroClass)
            return currentYabroViewWrapper

        val newInstance = FakeWebViewWrapper(yabroClass)
        webViewWrapper = newInstance
        return newInstance
    }

    override fun initYabroView() {
        // do nothing yet
    }

    override fun destroyYabroViewIfDetached(): Boolean {
        // do nothing yet
        return false
    }

}
