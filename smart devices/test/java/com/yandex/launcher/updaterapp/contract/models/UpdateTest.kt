package com.yandex.launcher.updaterapp.contract.models

import com.yandex.launcher.updaterapp.BaseRobolectricTest
import org.hamcrest.Matchers.equalTo
import org.hamcrest.MatcherAssert.assertThat
import org.junit.Test

class UpdateTest : BaseRobolectricTest() {

    @Test
    fun `serialized to Bundle, deserialized from Bundle`() {
        val appName = "some_appName"
        val packageName = "some_packageName"
        val downloadUrl = "some_url"
        val versionName = "some_version"
        val versionCode = 2021L
        val size = 1024L
        val localPath = "some_path"
        val installPriority = InstallPriority.FORCED
        val title = "some_title"
        val description = "some_description"
        val md5hash = "some_md5hash"
        val bitSettings = 1111L

        val origin = Update(
            appName = appName,
            packageName = packageName,
            downloadUrl = downloadUrl,
            versionName = versionName,
            versionCode = versionCode,
            size = size,
            localPath = localPath,
            installPriority = installPriority,
            title = title,
            description = description,
            md5hash = md5hash,
            bitSettings = bitSettings
        )

        val bundle = origin.toBundle()
        val deserialized = Update(bundle)


        assertThat(deserialized.appName, equalTo(appName))
        assertThat(deserialized.appName, equalTo(appName))
        assertThat(deserialized.packageName, equalTo(packageName))
        assertThat(deserialized.downloadUrl, equalTo(downloadUrl))
        assertThat(deserialized.versionName, equalTo(versionName))
        assertThat(deserialized.versionCode, equalTo(versionCode))
        assertThat(deserialized.size, equalTo(size))
        assertThat(deserialized.localPath, equalTo(localPath))
        assertThat(deserialized.installPriority, equalTo(installPriority))
        assertThat(deserialized.title, equalTo(title))
        assertThat(deserialized.description, equalTo(description))
        assertThat(deserialized.md5hash, equalTo(md5hash))
        assertThat(deserialized.bitSettings, equalTo(bitSettings))
    }
}
