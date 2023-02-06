formula = '''+|100| True | type.key
*|1.0|"баг блокирует использование функционала" in {} | userFactor
*|0.8|"баг создает неудобства"                  in {} | userFactor
*|0.1|"пользователь не видит баг"               in {} | userFactor
*|0.3|"косметический дефект"                    in {} | userFactor
*|0.5|"влияет на метрики продукта"              in {} | userFactor
*|1.0| "Основной"        == {} | zenFeatureFactor
*|0.5| "Важный"          == {} | zenFeatureFactor
*|0.25|"Вспомогательный" == {} | zenFeatureFactor
*|1.0| "PROD" == {} | stageFactor
*|0.5| "ABT"  == {} | stageFactor
*|1.0| "96085"  in {} | components[*].id # Авторизация
*|0.9| "104491" in {} | components[*].id # Главная
*|1.0| "96087"  in {} | components[*].id # Заказы
*|1.0| "96088"  in {} | components[*].id # Меню
*|1.0| "95960"  in {} | components[*].id # Пуши
*|0.8| "96086"  in {} | components[*].id # Рестораны
*|0.9| "96089"  in {} | components[*].id # Статистика
*|0.9| "96269"  in {} | components[*].id # Продвижение
*|0.8| "96091"  in {} | components[*].id # История заказов
*|0.8| "104494" in {} | components[*].id # Зоны доставки
*|0.5| "96099"  in {} | components[*].id # График работы
*|0.5| "96100"  in {} | components[*].id # Время готовки
*|0.9| "96093"  in {} | components[*].id # Акции
*|0.7| "96094"  in {} | components[*].id # Новости/Коммуникации
*|0.7| "96274"  in {} | components[*].id # Ваш сайт
*|0.5| "104496" in {} | components[*].id # База знаний
*|0.8| "96275"  in {} | components[*].id # Поддержка/Чаты поддержки
*|0.5| "104498" in {} | components[*].id # Прочее
*|0.2| "104500" in {} | components[*].id # restapp_mobile_web
*|1.0| "104501" in {} | components[*].id # restapp_desktop_web
*|0.8| "104502" in {} | components[*].id # restapp_ios
*|0.8| "104503" in {} | components[*].id # restapp_android
*|0.8| "96092"  in {} | components[*].id # restapp_cordova
*|1.0| "105467" in {} | components[*].id # restapp_all_web
*|10| {} >= 100 | THIS'''
