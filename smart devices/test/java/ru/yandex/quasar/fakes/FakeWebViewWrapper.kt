package ru.yandex.quasar.fakes

import android.graphics.Bitmap
import android.view.ViewGroup
import android.webkit.ValueCallback
import androidx.core.util.Consumer
import ru.yandex.quasar.app.webview.WebViewWrapper
import ru.yandex.quasar.app.webview.mordovia.MordoviaApp
import ru.yandex.quasar.app.webview.yabro.WebViewLoadingMetrics

class FakeWebViewWrapper(
        val yabroClass: Int
): WebViewWrapper {

    var newNavigationSessionStartedCount: Int = 0
    var navigationSessionSavesCount: Int = 0
    var loadUrlCalled: MutableList<LoadUrlItem> = mutableListOf()

    override fun loadUrl(url: String, scenario: String?, loadingMetrics: WebViewLoadingMetrics?) {
        loadUrlCalled.add(LoadUrlItem(url, scenario, loadingMetrics))
    }

    override fun evaluateJavascript(script: String?, resultCallback: ValueCallback<String>?) {
        // do nothing yet
    }

    override fun attachView(rootView: ViewGroup, layoutParams: ViewGroup.LayoutParams) {
        // do nothing yet
    }

    override fun detachViewSafe(rootView: ViewGroup) {
        // do nothing yet
    }

    override fun detachView() {
        // do nothing yet
    }

    override fun isAttached(): Boolean {
        // do nothing yet
        return false
    }

    override fun setupMordovia(mordoviaApp: MordoviaApp, loggableMeta: MutableMap<String, String>) {
        // do nothing yet
    }

    override fun hasActualType(yabroClass: Int): Boolean {
        // do nothing yet
        return false
    }

    override fun setPageStartedListener(pageStartedListener: Consumer<String>?) {
        // do nothing yet
    }

    override fun addPageCompletelyFinishedListener(pageCompletelyFinishedListener: Consumer<String>) {
        // do nothing yet
    }

    override fun setLoadPreparationsStartedListener(loadPreparationsStartedListener: Consumer<String>?) {
        // do nothing yet
    }

    override fun setPageLoadUrlCalledListener(pageLoadUrlCalledListener: Consumer<String>?) {
        // do nothing yet
    }

    override fun setErrorViewShowListener(errorViewShowListener: Consumer<Int>?) {
        // do nothing yet
    }

    override fun setErrorViewDismissedListener(errorViewDismissedListener: Runnable?) {
        // do nothing yet
    }

    override fun showErrorView(loadState: Int) {
        // do nothing yet
    }

    override fun makeSnapshot(snapshotConsumer: Consumer<Bitmap>) {
        snapshotConsumer.accept(Bitmap.createBitmap(1, 1, Bitmap.Config.RGB_565))
    }

    override fun getHistory(): MutableList<String> {
        // do nothing yet
        return mutableListOf()
    }

    override fun goBackToUrl(url: String): Boolean {
        // do nothing yet
        return false
    }

    override fun goBack(): Boolean {
        // do nothing yet
        return false
    }

    override fun setUpdateVisitedHistoryListener(listener: Runnable?) {
        // do nothing yet
    }

    override fun dropLeastSavedHistory(scenario: String?) {
        // do nothing yet
    }

    override fun dropFirstSavedHistory(scenario: String?) {
        // do nothing yet
    }

    override fun saveNavigationState() {
        navigationSessionSavesCount += 1
    }

    override fun restoreNavigationState(scenario: String?) {
        // do nothing yet
    }

    override fun startNewNavigationState() {
        newNavigationSessionStartedCount += 1
    }

    override fun setContentReadyListener(contentReadyListener: Runnable?) {
        // do nothing yet
    }

    override fun getUrl(): String {
        return if (loadUrlCalled.isEmpty()) "" else loadUrlCalled.last().url
    }

    override fun getScenario(): String? {
        return if (loadUrlCalled.isEmpty()) null else loadUrlCalled.last().scenario
    }

    data class LoadUrlItem(val url: String, val scenario: String?, val loadingMetrics: WebViewLoadingMetrics?)
}
