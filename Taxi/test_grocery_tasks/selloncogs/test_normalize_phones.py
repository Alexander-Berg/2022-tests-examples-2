import pandas as pd

from grocery_tasks.selloncogs.utils.normalize_phones import normalize_phones


def test_normalize_phones():
    expected_result = pd.DataFrame(
        [
            ('+791348729046', 'Russia', ''),
            ('9153904925', 'Russia', '+79153904925'),
            ('88005553535', 'Russia', ''),
            ('89261112233', 'Russia', '+79261112233'),
            ('+79184308459', 'Russia', '+79184308459'),
            ('+19184308459', 'Russia', ''),
            ('kfssd9023', 'Russia', ''),
            ('7', 'Russia', ''),
            ('+7', 'Russia', ''),
            ('8', 'Russia', ''),
            ('9', 'Russia', ''),
            ('ksdflsjga915kdsf490lasdjf49fadsflj25', 'Russia', '+79154904925'),
            ('Удивлённый Иван', 'Russia', ''),
            ('7', 'Israel', ''),
            ('+975537130692', 'Israel', ''),
            ('9', 'Israel', ''),
            ('+7', 'Israel', ''),
            ('+9', 'Israel', ''),
            ('+97', 'Israel', ''),
            ('+972153904925', 'Israel', '+972153904925'),
            ('+973153904925', 'Israel', ''),
            ('+873153904925', 'Israel', ''),
            ('+153904925', 'Israel', ''),
            ('+2153904925', 'Israel', '+972153904925'),
            ('+72153904925', 'Israel', '+972153904925'),
            ('Удивлённый Изя', 'Israel', ''),
            ('97звони200дяде555Яше3535', 'Israel', '+972005553535'),
            ('33', 'France', ''),
            ('+33', 'France', ''),
            ('+33805553535', 'France', '+33805553535'),
            ('+32805553535', 'France', '+33805553535'),
            ('33153904925', 'France', '+33153904925'),
            ('Удивлённый Жак', 'France', ''),
            ('', 'France', ''),
            ('Луиза88,я777полюбил66другую55', 'France', '+33887776655'),
            ('44', 'United Kingdom', ''),
            ('+44', 'United Kingdom', ''),
            ('+449153904926', 'United Kingdom', '+449153904926'),
            ('+469153904925', 'United Kingdom', '+449153904925'),
            (
                '43Джон800,ты555выпил35мою35пинту',
                'United Kingdom',
                '+448005553535',
            ),
            ('443354456728', 'United Kingdom', '+443354456728'),
            ('+459205897330', 'United Kingdom', '+449205897330'),
            ('Удивлённый Фред', 'United Kingdom', ''),
        ],
        columns=['phone', 'region_name', 'normalized_phone'],
    )
    result = normalize_phones(expected_result[['phone', 'region_name']])
    pd.testing.assert_frame_equal(result, expected_result)
