# -*- coding: utf-8 -*-
import difflib


def levenshteinDistance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1
    distances = list(range(len(s1) + 1))
    for i2, c2 in enumerate(s2):
        distances_ = [i2 + 1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


a = 'ПАСПОРТНО-ВИЗОВЫМ ОТДЕЛЕНИЕМ ОВД РАЙОНА НОВО-ПЕРЕДЕЛКИНО Г. МОСКВЫ'.lower()
b = 'с и и с к а я е д е р а ц и я отделом внутренних дел района ново-переделкино увд зао города москвы 15.05.2003 Код подралдело 772-037 co Личшай код Фажили цыганов Имя иван Отчество анатольевич Пол Место рождения Дата МУЖ. рождения 01.02.1983 город москва co'.lower()
print((len(b) - levenshteinDistance(a, b)))
