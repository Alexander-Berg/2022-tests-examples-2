package com.yandex.tv.services.testapp

import android.app.Activity
import android.os.Bundle
import android.view.ViewGroup
import android.widget.FrameLayout

/**
 * Activity can be used to test leaking behavior of sdk manually.
 * 1) start activity
 * 2) press back
 * 3) force GC
 * 4) dump heap
 *
 * Sdk is expected to NOT leak the activity.
 * ART seems to be able to properly clean leaked connection and whole sdk.
 *
 * Tests on emulator API 25, 28 show that calling shutdownNow() in sdk's finalize()
 * prevents sdk from collecting during first GC (still will be collected during next GC).
 * Sdk with default finalize() implementation gets collected during first GC.
 */
class TestActivity : Activity() {

    var sdk: TestServiceSdk2? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(FrameLayout(this), ViewGroup.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT))

        sdk = TestServiceSdk2.Factory.create(this, "com.yandex.tv.services.testapp")

        // trigger binding
        sdk!!.getConstantString()
    }

}
