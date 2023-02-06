package com.yandex.launcher.updaterapp

import android.os.Parcel
import com.yandex.launcher.updaterapp.contract.models.InstallRequest
import org.hamcrest.Matchers.`is`
import org.hamcrest.Matchers.not
import org.hamcrest.Matchers.nullValue
import org.hamcrest.MatcherAssert.assertThat
import org.junit.Test


class InstallRequestTest : BaseRobolectricTest() {

    @Test
    fun shouldConvertNullableFieldsToEmptyText() {
        val request = InstallRequest(
            "url", "packageName",
            null, null, null, null, false
        )

        assertThat(request.downloadUrl, not(nullValue()))
        assertThat(request.packageName, not(nullValue()))
        assertThat(request.name, not(nullValue()))
        assertThat(request.iconUrl, not(nullValue()))
        assertThat(request.description, not(nullValue()))
        assertThat(request.trackingUrl, not(nullValue()))
    }

    @Test
    fun shouldVerifyParcelableWriteRead() {
        val request = InstallRequest(
            "url", "packageName",
            "name", "iconUrl", "description", "trackingUrl", false
        )
        val parcel = Parcel.obtain()
        val resultRequest: InstallRequest

        request.writeToParcel(parcel, 0)

        parcel.setDataPosition(0)
        resultRequest = InstallRequest.CREATOR.createFromParcel(parcel)

        assertThat(request, `is`(resultRequest))
    }

    @Test
    fun shouldVerifySameHashForEqualsObjects() {
        val request1 = InstallRequest(
            "url", "packageName",
            "name", "iconUrl", "description", "trackingUrl", true
        )
        val request2 = InstallRequest(
            "url", "packageName",
            "name", "iconUrl", "description", "trackingUrl", true
        )

        assertThat(request1, `is`(request2))
        assertThat(request1.hashCode(), `is`(request2.hashCode()))
    }

    @Test
    fun shouldDescribeContentReturnZero() {
        val request = InstallRequest(
            "url", "packageName",
            "name", "iconUrl", "description", "trackingUrl", false
        )

        assertThat(request.describeContents(), `is`(0))
    }
}
