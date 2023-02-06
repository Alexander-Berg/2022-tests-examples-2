import pytest
from libstall.util.barcode import true_mark_unpack


@pytest.mark.parametrize(
    'code,answer',
    [
        (  # легпром
            '<FNC1>010460780959150821sSBmxTYIFT(eq<GS>91FFD0<GS>92'
            'testtesttesttesttesttesttesttesttesttesttesttesttestt'
            'esttesttesttesttesttesttesttesttest',
            {
                'barcode': '4607809591508',
                'serial': 'sSBmxTYIFT(eq',
                'id_check_key': 'FFD0',
                'check_big':
                    'testtesttesttesttesttesttesttesttesttesttestt'
                    'esttesttesttesttesttesttesttesttesttesttest',
            }
        ),
        (  # духи и туалетная вода
            '<FNC1>010460780959133121e/Fw:xeo47NK2<GS>91F010<GS>92'
            'Afwuf6d3c9oszbRy/Vb+hRUl1wokz/8UOthdpBYw9A0=',
            {
                'barcode': '4607809591331',
                'serial': 'e/Fw:xeo47NK2',
                'id_check_key': 'F010',
                'check_big':
                    'Afwuf6d3c9oszbRy/Vb+hRUl1wokz/8UOthdpBYw9A0=',
            }
        ),
        (  # молочная продукция
            '<FNC1>0103041094787443215Qbag!<GS>93Zjqw',
            {
                'barcode': '3041094787443',
                'serial': '5Qbag!',
                'check_small': 'Zjqw',
            }
        ),
        (  # молочная продукция с весом
            '<FNC1>0103041094787443215Qbag!<GS>93Zjqw<GS>3103000353',
            {
                'barcode': '3041094787443',
                'serial': '5Qbag!',
                'check_small': 'Zjqw',
                'weight': '000353',
            }
        ),
        (  # упакованная вода
            '<FNC1>010460780959152221p=s&jq:0F:CWq<GS>930I1N',
            {
                'barcode': '4607809591522',
                'serial': 'p=s&jq:0F:CWq',
                'check_small': '0I1N',
            }
        ),
        (  # говнишко1
            '<FNC1>010460880959152222лол<GS>93лолллл',
            None
        ),
        (  # говнишко2
            '<FNC1>01046088095915',
            None
        ),
        (  # говнишко3
            '<FNC1>020460880959152222лол<GS>93лолллл',
            None
        ),
        (  # говнишко4
            '<FNC1>0103041094787443215Qbag!<GS>93Zjqw<GS>99ssa',
            None
        ),
    ]
)
def test_true_mark_unpack(tap, code, answer):
    with tap.plan(1, 'проверяем коррекность парсинга честного знака'):
        if code.startswith('<FNC1>'):
            code = code[6:]
        code = code.replace('<GS>', chr(29))
        algo_res = true_mark_unpack(code)
        tap.eq(algo_res, answer, 'правильно распарсили')
