import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

buildscript {
    apply(from = "../gradle/scripts/global.gradle.kts")
    val kotlinVersion: String by project.extra
    val taxiInfraVersion: String by project.extra

    repositories {
        google()
        mavenLocal()
        mavenCentral()
        maven("https://plugins.gradle.org/m2")
        maven("https://artifactory-ext.yandex.net/yandex_mobile_releases") {
            credentials(HttpHeaderCredentials::class) {
                name = "Authorization"
                value = "OAuth ${System.getenv("YA_ARTIFACTORY_TOKEN")}"
            }
            authentication {
                create<HttpHeaderAuthentication>("header")
            }
        }
        maven("https://artifactory-ext.yandex.net/yandex_mobile_snapshots") {
            credentials(HttpHeaderCredentials::class) {
                name = "Authorization"
                value = "OAuth ${System.getenv("YA_ARTIFACTORY_TOKEN")}"
            }
            authentication {
                create<HttpHeaderAuthentication>("header")
            }
        }
    }

    dependencies {
        classpath(kotlin("gradle-plugin", kotlinVersion))
        classpath("ru.yandex.taxi.infra:maven-gradle:$taxiInfraVersion")
    }
}

plugins {
    kotlin("jvm") version "1.5.10"
    id("ru.yandex.pro-build.swagger")
}

allprojects {
    repositories {
        mavenCentral()
    }
}

swaggerCodegen {
    targetPackage = "ru.yandex.taxi.swagger.test"
    sourceDirectory = "src/test/swagger"
    enumPropertyNaming = "UPPERCASE"
    skippedHeaderParams = setOf("Accept-Language")
    skippedQueryParams = setOf("park_id")
    rootYamlFiles = setOf(
        "additionalProperties-true-allOf.yaml",
        "common.yaml",
        "inline-builtin-types.yaml",
        "ref-additional-props.yaml",
        "sealed-class.yaml",
        "sealed-class-by-discriminator.yaml",
        "ref-enum-discriminator.yaml"
    )
}

dependencies {
    apply(from = "../gradle/scripts/global.gradle.kts")

    val mockServerVersion: String by project.extra
    val mockWebServerVersion: String by project.extra
    val gsonVersion: String by project.extra
    val rxJavaVersion: String by project.extra

    implementation(kotlin("stdlib-jdk8"))
    implementation(project(":swagger-http-client"))
    implementation(project(":swagger-kotlin-codegen"))
    implementation("com.google.code.gson:gson:$gsonVersion")
    implementation("io.reactivex.rxjava2:rxjava:$rxJavaVersion")

    implementation("junit:junit:4.12")

    testImplementation("org.mock-server:mockserver-netty:$mockServerVersion")
    testImplementation("com.squareup.okhttp3:mockwebserver:$mockWebServerVersion")

    testRuntimeOnly("org.junit.vintage:junit-vintage-engine:5.7.0")
}

tasks.test {
    useJUnitPlatform()
    testLogging {
        events("passed", "skipped", "failed")
    }
}

tasks.withType<KotlinCompile>().configureEach {
    kotlinOptions.jvmTarget = JavaVersion.VERSION_11.toString()
}