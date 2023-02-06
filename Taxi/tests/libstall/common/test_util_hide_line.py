from libstall.util import hide_part_of_line


def test_hide_part_of_line(tap):
    with tap.plan(13, "Экранирование части строки"):
        tap.eq(hide_part_of_line("+78005553535"),
               "+78xxxxxx535",
               "номер телефона без параметров")

        tap.eq(hide_part_of_line("+78005553535", start_cnt=3),
               "+78xxxxxxxxx",
               "номер телефона c показанной частью в начале")

        tap.eq(hide_part_of_line("+78005553535", end_cnt=3),
               "xxxxxxxxx535",
               "номер телефона c показанной частью в конце")

        tap.eq(hide_part_of_line("+78005553535", start_cnt=5, end_cnt=3),
               "+7800xxxx535",
               "номер телефона c параметрами")

        tap.eq(hide_part_of_line("78005553535"),
               "78xxxxxxx35",
               "с нечетным количеством символов, без параметров")

        tap.eq(hide_part_of_line("78005553535", start_cnt=8),
               "78005553xxx",
               "с нечетным количеством символов, c показанной частью в начале")

        tap.eq(hide_part_of_line("78005553535", end_cnt=8),
               "xxx05553535",
               "с нечетным количеством символов, c показанной частью в конце")

        tap.eq(hide_part_of_line("78005553535", start_cnt=5, end_cnt=4),
               "78005xx3535",
               "с нечетным количеством символов, c параметрами")

        tap.eq(hide_part_of_line("78005553535", start_cnt=11),
               "78005553535", "Количество символов в начале больше или "
                              "равно длине строки")

        tap.eq(hide_part_of_line("78005553535", end_cnt=11),
               "78005553535", "Количество символов в конце больше или равно "
                              "длине строки")

        tap.eq(hide_part_of_line("78005553535", start_cnt=5, end_cnt=6),
               "78005553535", "Количество символов в конце и начале "
                     "больше или равно длине строки")

        tap.eq(hide_part_of_line(""),
               "", "Пустая строка")

        tap.eq(hide_part_of_line(1234), 1234, "на вход получаеют не строку")
