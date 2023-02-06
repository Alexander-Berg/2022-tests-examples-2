# -*- coding: utf-8 -*-
import base64
import zlib


TEST_IDP_DOMAIN = 'sso-adfs-test-domain.com'  # название домена
TEST_IDP_DOMAIN_ID = 2997121  # id домена sso-adfs-test-domain.com в тестинге
TEST_IDP_SSO_NETLOC = 'sso-adfs-test.beleckiy.ru'  # локация в которую ходим чтоб авторизоваться в данном домене
TEST_RELAYSTATE = 'https://0.0.0.0:8000/'
TEST_TRACK = 'f154ce6b02d23baa28e1103e221614357f'  # трек зашит в ответе
TEST_EMAIL = 'berd_email@sso-adfs-test-domain.com'
TEST_NAME_ID = 'berd@sso-adfs-test-domain.com'
TEST_LOGIN = 'berd'
TEST_FEDERAL_ALIAS_VALUE = '%s/berd' % TEST_IDP_DOMAIN_ID
TEST_PDD_ALIAS_VALUE = '%s/berd_email' % TEST_IDP_DOMAIN_ID

TEST_SAML_RESPONSE = ('PHNhbWxwOlJlc3BvbnNlIElEPSJfOTFkNGIxYzItMzM2NS00OGMyLTk3OTUtYzExMzI5ZGVkZmEwIiBW'
                      'ZXJzaW9uPSIyLjAiIElzc3VlSW5zdGFudD0iMjAyMS0xMC0yMFQxNDo1MDowNy4wNjdaIiBEZXN0aW5h'
                      'dGlvbj0iaHR0cHM6Ly9wYXNzcG9ydC10ZXN0LnlhbmRleC5ydS9hdXRoL3Nzby9jb21taXQiIENvbnNl'
                      'bnQ9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDpjb25zZW50OnVuc3BlY2lmaWVkIiBJblJlc3Bv'
                      'bnNlVG89InRyYWNrX2YxNTRjZTZiMDJkMjNiYWEyOGUxMTAzZTIyMTYxNDM1N2YiIHhtbG5zOnNhbWxw'
                      'PSJ1cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6cHJvdG9jb2wiPjxJc3N1ZXIgeG1sbnM9InVybjpv'
                      'YXNpczpuYW1lczp0YzpTQU1MOjIuMDphc3NlcnRpb24iPmh0dHA6Ly9zc28tYWRmcy10ZXN0LmJlbGVj'
                      'a2l5LnJ1L2FkZnMvc2VydmljZXMvdHJ1c3Q8L0lzc3Vlcj48c2FtbHA6U3RhdHVzPjxzYW1scDpTdGF0'
                      'dXNDb2RlIFZhbHVlPSJ1cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6c3RhdHVzOlN1Y2Nlc3MiIC8+'
                      'PC9zYW1scDpTdGF0dXM+PEFzc2VydGlvbiBJRD0iXzRhN2QzOTljLTlhYjMtNGE4Yi1hYmUzLTRkNWY4'
                      'ZTgxMDg3ZiIgSXNzdWVJbnN0YW50PSIyMDIxLTEwLTIwVDE0OjUwOjA3LjA2N1oiIFZlcnNpb249IjIu'
                      'MCIgeG1sbnM9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDphc3NlcnRpb24iPjxJc3N1ZXI+aHR0'
                      'cDovL3Nzby1hZGZzLXRlc3QuYmVsZWNraXkucnUvYWRmcy9zZXJ2aWNlcy90cnVzdDwvSXNzdWVyPjxk'
                      'czpTaWduYXR1cmUgeG1sbnM6ZHM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvMDkveG1sZHNpZyMiPjxk'
                      'czpTaWduZWRJbmZvPjxkczpDYW5vbmljYWxpemF0aW9uTWV0aG9kIEFsZ29yaXRobT0iaHR0cDovL3d3'
                      'dy53My5vcmcvMjAwMS8xMC94bWwtZXhjLWMxNG4jIiAvPjxkczpTaWduYXR1cmVNZXRob2QgQWxnb3Jp'
                      'dGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzA0L3htbGRzaWctbW9yZSNyc2Etc2hhMjU2IiAvPjxk'
                      'czpSZWZlcmVuY2UgVVJJPSIjXzRhN2QzOTljLTlhYjMtNGE4Yi1hYmUzLTRkNWY4ZTgxMDg3ZiI+PGRz'
                      'OlRyYW5zZm9ybXM+PGRzOlRyYW5zZm9ybSBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDAv'
                      'MDkveG1sZHNpZyNlbnZlbG9wZWQtc2lnbmF0dXJlIiAvPjxkczpUcmFuc2Zvcm0gQWxnb3JpdGhtPSJo'
                      'dHRwOi8vd3d3LnczLm9yZy8yMDAxLzEwL3htbC1leGMtYzE0biMiIC8+PC9kczpUcmFuc2Zvcm1zPjxk'
                      'czpEaWdlc3RNZXRob2QgQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzA0L3htbGVuYyNz'
                      'aGEyNTYiIC8+PGRzOkRpZ2VzdFZhbHVlPiswd2hXamVjbi9NT1Z5Y0tNM2Y5aVIvOGIwSTd6bWNhTWdn'
                      'MXRkZWtBbHc9PC9kczpEaWdlc3RWYWx1ZT48L2RzOlJlZmVyZW5jZT48L2RzOlNpZ25lZEluZm8+PGRz'
                      'OlNpZ25hdHVyZVZhbHVlPlgwd2gvS2hoY0lhcitvM1JhWWhtMDJzbFZ3Ym9Ta0Z1ck93SXowRE5SVDF6'
                      'WnpCNkozMzM4SlVobWhCa09GU1lCa2h3VStYTng5Zyt6SkdYWU1COWRub2cwazhJdC9PTmIveW13NEVn'
                      'ZXpoZjJ3REw1cFRybVJtbzMxY2JkbXQ5bXRFWHpFd0tkR0ZMdFYxd2hXalBnYjVRdlZLR0hTd0l2SU5w'
                      'ejNXWU9rYVBMbUZlckV4cUkrcEFWanJTRm9hUHJ2WGZJc2NRenZTVExXclVLU25uZWlFWUNCaGJMbGMx'
                      'VkY4eFRhaTFGYkRRSHNBcmhqZGlZOFpxMTdkK1hNelVZZVY4R2o0QTdQMXRWZ2NLTGdDZlJ3UmNzY0d1'
                      'NHYvbWllQjhBSmVWUjhtWDVsN1hObUVhQm1XYjhMM1lIYU03R1VQdW5RdWtrM21IMmV6ZEVzdkZ2Zz09'
                      'PC9kczpTaWduYXR1cmVWYWx1ZT48S2V5SW5mbyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8w'
                      'OS94bWxkc2lnIyI+PGRzOlg1MDlEYXRhPjxkczpYNTA5Q2VydGlmaWNhdGU+TUlJQzdqQ0NBZGFnQXdJ'
                      'QkFnSVFRSDRGRk9sSXFhRkRjaUpHVlBnMjZ6QU5CZ2txaGtpRzl3MEJBUXNGQURBek1URXdMd1lEVlFR'
                      'REV5aEJSRVpUSUZOcFoyNXBibWNnTFNCemMyOHRZV1JtY3kxMFpYTjBMbUpsYkdWamEybDVMbkoxTUI0'
                      'WERUSXhNRGN5T1RFMk1EVTFNbG9YRFRJeU1EY3lPVEUyTURVMU1sb3dNekV4TUM4R0ExVUVBeE1vUVVS'
                      'R1V5QlRhV2R1YVc1bklDMGdjM052TFdGa1puTXRkR1Z6ZEM1aVpXeGxZMnRwZVM1eWRUQ0NBU0l3RFFZ'
                      'SktvWklodmNOQVFFQkJRQURnZ0VQQURDQ0FRb0NnZ0VCQUx1SmFyMVUxamxIbkxxblZGN054M2pPV0cz'
                      'b0gwSDVNN250cForOWpCWHJKZFo2OGM2dEw1eW9ocUlCRE1jRmswYllDVk1oazI4QWZnWVlxRVdlejlU'
                      'RTA4WTd4bjI4cW1ZL094cUxTNVYvTmJsSUVDaUgwZzRRNWhhNXhaYWM3U25hbzdHL3BQRmxEZDQwNm1y'
                      'd0QzV3gxT3F0T1JnWFNwM1FQc1R2WmtVMG5wMzN0UkNFUUgyb2JUd1duNXd0WmtQMm5Mb2hHY1NJOVU1'
                      'NXBhMFpXRTZhR0tkREZtT0svaUJCNmVaUnFPZXhmS3FSV05aaUdORU9zWUNReXFnQ2dCL0hQTkhYcEt0'
                      'b2lHRFpxbkVyeS8wUlNBdlprNGR1TnFpNFVocnJ2TzRJNHk2cGRoaEhwUklKWTNRQkk0ZHpJTkpzN0VJ'
                      'bUV2cStMRGlzcW52QkpUVUNBd0VBQVRBTkJna3Foa2lHOXcwQkFRc0ZBQU9DQVFFQUsxdmNCMWc0Tk0y'
                      'ZU82amlzdkQ5Z1RsYTVZM092NWorUnVIZmJxT1c3VmNQMU16cmFuNFdxSnJKZGRhYThZZitta1h5ZjYy'
                      'b21FMjYwWlpLbjNaZDNldmdGUThFWHVqT3l6ajNCOHZnN2Q5MEZYVzRVbzBqR0h0dlR0VWFoUVB0VG9B'
                      'TGhWaEdtUWVJTnFrdTV3Y3VMa3gyYzl6aGtwVThYWFFVekRnOXpCd01iVmc3ZWlEaDZFSFdhYVBXK085'
                      'K0x0cGdPcUVLWHFYb1JsZ3RaTW5zSTNTWTJiTnkrTzRSSE94d0tRSFpSdUZ3ckNyNlR4cUptYzNiUlBt'
                      'Z2gzcnpndXB3VXJtVm5EL2lMZ0FndTJMM0svWjdTWkN5SUtvbnVPS2ZGU2xEVWpWRkREajd1My91L1Mr'
                      'alVwVDJYaGwyZExVaVEwREZuOURIMnNXQjlNRWNkZz09PC9kczpYNTA5Q2VydGlmaWNhdGU+PC9kczpY'
                      'NTA5RGF0YT48L0tleUluZm8+PC9kczpTaWduYXR1cmU+PFN1YmplY3Q+PE5hbWVJRCBGb3JtYXQ9InVy'
                      'bjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDpuYW1laWQtZm9ybWF0OnRyYW5zaWVudCI+YmVyZEBzc28t'
                      'YWRmcy10ZXN0LWRvbWFpbi5jb208L05hbWVJRD48U3ViamVjdENvbmZpcm1hdGlvbiBNZXRob2Q9InVy'
                      'bjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDpjbTpiZWFyZXIiPjxTdWJqZWN0Q29uZmlybWF0aW9uRGF0'
                      'YSBJblJlc3BvbnNlVG89InRyYWNrX2YxNTRjZTZiMDJkMjNiYWEyOGUxMTAzZTIyMTYxNDM1N2YiIE5v'
                      'dE9uT3JBZnRlcj0iMjAyMS0xMC0yMFQxNDo1NTowNy4wNjdaIiBSZWNpcGllbnQ9Imh0dHBzOi8vcGFz'
                      'c3BvcnQtdGVzdC55YW5kZXgucnUvYXV0aC9zc28vY29tbWl0IiAvPjwvU3ViamVjdENvbmZpcm1hdGlv'
                      'bj48L1N1YmplY3Q+PENvbmRpdGlvbnMgTm90QmVmb3JlPSIyMDIxLTEwLTIwVDE0OjUwOjA3LjA1MVoi'
                      'IE5vdE9uT3JBZnRlcj0iMjAyMS0xMC0yMFQxNTo1MDowNy4wNTFaIj48QXVkaWVuY2VSZXN0cmljdGlv'
                      'bj48QXVkaWVuY2U+aHR0cDovLzAuMC4wLjE6ODAwMC88L0F1ZGllbmNlPjwvQXVkaWVuY2VSZXN0cmlj'
                      'dGlvbj48L0NvbmRpdGlvbnM+PEF0dHJpYnV0ZVN0YXRlbWVudD48QXR0cmlidXRlIE5hbWU9IlVzZXIu'
                      'Rmlyc3RuYW1lIj48QXR0cmlidXRlVmFsdWU+0J7Qs9GD0LvRjNCz0LXRgNC10Lo8L0F0dHJpYnV0ZVZh'
                      'bHVlPjwvQXR0cmlidXRlPjxBdHRyaWJ1dGUgTmFtZT0iVXNlci5TdXJuYW1lIj48QXR0cmlidXRlVmFs'
                      'dWU+0JHQtdGA0LTRi9C80YPRhdCw0LzQtdC00L7QstCwPC9BdHRyaWJ1dGVWYWx1ZT48L0F0dHJpYnV0'
                      'ZT48QXR0cmlidXRlIE5hbWU9IlVzZXIuRW1haWxBZGRyZXNzIj48QXR0cmlidXRlVmFsdWU+YmVyZF9l'
                      'bWFpbEBzc28tYWRmcy10ZXN0LWRvbWFpbi5jb208L0F0dHJpYnV0ZVZhbHVlPjwvQXR0cmlidXRlPjwv'
                      'QXR0cmlidXRlU3RhdGVtZW50PjxBdXRoblN0YXRlbWVudCBBdXRobkluc3RhbnQ9IjIwMjEtMTAtMjBU'
                      'MTI6NDM6NDEuMTk1WiIgU2Vzc2lvbkluZGV4PSJfNGE3ZDM5OWMtOWFiMy00YThiLWFiZTMtNGQ1Zjhl'
                      'ODEwODdmIj48QXV0aG5Db250ZXh0PjxBdXRobkNvbnRleHRDbGFzc1JlZj51cm46b2FzaXM6bmFtZXM6'
                      'dGM6U0FNTDoyLjA6YWM6Y2xhc3NlczpQYXNzd29yZFByb3RlY3RlZFRyYW5zcG9ydDwvQXV0aG5Db250'
                      'ZXh0Q2xhc3NSZWY+PC9BdXRobkNvbnRleHQ+PC9BdXRoblN0YXRlbWVudD48L0Fzc2VydGlvbj48L3Nh'
                      'bWxwOlJlc3BvbnNlPg==')

TEST_LOGOUT_REQUEST_TEMPLATE = '''<samlp:LogoutRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                                                       xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
                                                       ID="ONELOGIN_e6fe100bc58da3e3fbab166e90c6544f152aba82"
                                                       Version="2.0"
                                                       IssueInstant="{date_time}"
                                                       Destination="https://passport-test.yandex.ru/auth/sso/logout"
                                                       >
                                      <saml:Issuer>http://sso-adfs-test.beleckiy.ru/adfs/services/trust</saml:Issuer>
                                      <saml:NameID Format="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent">{name_id}</saml:NameID>
                                      <samlp:SessionIndex>_e8025ad4-865e-42a9-9b7d-9b9804647a1b</samlp:SessionIndex>
                                  </samlp:LogoutRequest>'''

TEST_LOGOUT_REQUEST = base64.b64encode(zlib.compress(TEST_LOGOUT_REQUEST_TEMPLATE.format(name_id=TEST_NAME_ID, date_time='2021-12-11T14:39:03Z').encode('utf-8'))[2:-4])
