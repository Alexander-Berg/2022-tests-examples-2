import allure
import pytest
import time

from screens.android_go_screen import AndroidGoScreen
from screens.android_taximeter_screen import AndroidTaximeterScreen
from allure_commons.types import AttachmentType


@allure.suite('Mobile Tests')
@allure.severity(allure.severity_level.CRITICAL)
@allure.title('Проверка получения пуш-нотификаций на android-эмуляторе.')
@pytest.mark.parametrize("app", [
    pytest.param("pro", marks=pytest.mark.driver_integration, id="Android Pro"),
    pytest.param("go", marks=pytest.mark.user_integration, id="Android Go")
])
def test_wait_for_push_notifications(appium_driver, custom_param, app):
    notification_text = f"Hello from test!{custom_param}"

    with allure.step(f"Авторизуемся в {app} под пользователем, который есть в тестовом сегменте."):
        if app == "go":
            notification_text = notification_text + "3"  # в тестовом сегменте у тестового пользователя должен быть такой текст коммуникации
            android_screen = AndroidGoScreen(appium_driver)
            time.sleep(3)
            # android_screen.set_location()
            android_screen.gdpr_accept()
            android_screen.change_address()
            sc = android_screen.get_screenshot()
            allure.attach(sc, 'app_opened', AttachmentType.PNG)
            time.sleep(5)
            android_screen.open_menu()
            sc = android_screen.get_screenshot()
            allure.attach(sc, 'open_menu', AttachmentType.PNG)
            if not android_screen.is_user_logged_in():
                android_screen.close_banner()
                android_screen.choose_enter_phone()
                sc = android_screen.get_screenshot()
                allure.attach(sc, 'choose_enter_phone', AttachmentType.PNG)
                android_screen.log_into_yandex_id(login="yndx-dlopteva-kmuiyx", password="gen3244")
                time.sleep(15)

            sc = android_screen.get_screenshot()
            allure.attach(sc, 'logged_in', AttachmentType.PNG)
        elif app == "pro":
            notification_text = notification_text + "1"  # в тестовом сегменте у тестового пользователя должен быть такой текст коммуникации
            android_screen = AndroidTaximeterScreen(appium_driver)
            android_screen.click_continue()
            android_screen.click_understand()
            android_screen.input_phone("0009822521")
            android_screen.click_login()
            android_screen.choose_park()
            time.sleep(30)
            sc = android_screen.get_screenshot()
            allure.attach(sc, 'logged_in', AttachmentType.PNG)

    with allure.step("Открываем панель уведомлений и ждем, когда придет первая пуш-нотификация "
                     "(кампания на этапе Тестирование)."):
        android_screen.open_notification_panel()
        # Первый пуш - после Тестирования кампании
        android_screen.wait_for_notification_with_text(notification_text, match_type="starts_with")
        sc = android_screen.get_screenshot()
        allure.attach(sc, 'get_test_push', AttachmentType.PNG)

    with allure.step("Очищаем нотификации."):
        android_screen.clear_notifications()
        time.sleep(2)
        android_screen.open_notification_panel()
        sc = android_screen.get_screenshot()
        allure.attach(sc, 'cleaned_notifications', AttachmentType.PNG)

    with allure.step("Ждем вторую пуш-нотификацию (кампания на этапе Отправка)."):
        # Второй пуш - после Отправки кампании
        android_screen.wait_for_notification_with_text(notification_text, timeout=1800)
        sc = android_screen.get_screenshot()
        allure.attach(sc, 'get_sent_push', AttachmentType.PNG)
        android_screen.close_notification_panel()
