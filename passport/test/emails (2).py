# -*- coding: utf-8 -*-

from passport.backend.core.mailer.faker.mail_utils import assert_email_message_sent


DEALIASIFY_NOTIFICATION_SUBJECT_RUSSIAN = u'В ваш аккаунт теперь нельзя войти по номеру телефона'
REALIASIFY_NOTIFICATION_SUBJECT_RUSSIAN = u'Телефон {alias} теперь привязан к другому аккаунту'.format

SECURE_PHONE_REMOVAL_STARTED_NOTIFICATION_SUBJECT_ENGLISH = u'The phone number linked to the Yandex account will be deleted in 14\n days'
SECURE_PHONE_REMOVAL_STARTED_NOTIFICATION_SUBJECT_RUSSIAN = u'Привязанный к аккаунту на Яндексе номер будет удалён через 14 дней'

SECURE_PHONE_REMOVED_WITH_QUARANTINE_NOTIFICATION_SUBJECT_RUSSIAN = u'Удалён телефонный номер, привязанный к аккаунту на Яндексе'
SECURE_PHONE_REMOVED_WITHOUT_QUARANTINE_NOTIFICATION_SUBJECT_RUSSIAN = u'Привязанный к аккаунту на Яндексе телефонный номер удален'
SECURE_PHONE_REMOVED_WITHOUT_QUARANTINE_NOTIFICATION_SUBJECT_ENGLISH = u'The phone number linked to your Yandex account has been removed'

SECURE_PHONE_REPLACEMENT_STARTED_NOTIFICATION_SUBJECT_ENGLISH = u'The phone number linked to your Yandex account will be changed in 14\n days'
SECURE_PHONE_REPLACEMENT_STARTED_NOTIFICATION_SUBJECT_RUSSIAN = u'Привязанный к аккаунту на Яндексе телефонный номер будет изменён через 14 дней'

SECURE_PHONE_REPLACED_SUBJECT_ENGLISH = u'The phone number linked to your Yandex account has been changed'
SECURE_PHONE_REPLACED_SUBJECT_RUSSIAN = u'Привязанный к аккаунту на Яндексе телефонный номер изменён'

SECURE_PHONE_BOUND_NOTIFICATION_SUBJECT_ENGLISH = u'A phone number has been linked to your Yandex account'
SECURE_PHONE_BOUND_NOTIFICATION_SUBJECT_RUSSIAN = u'К аккаунту на Яндексе привязан телефонный номер'


def SECURE_PHONE_BOUND_NOTIFICATION_BODY_ENGLISH(firstname, login):
    return u'''
    <!DOCTYPE html>
    <html>
    <head>
      <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
      <title></title>
      <style>
        .mail-address a,
        .mail-address a[href] {
          text-decoration: none !important;
          color: #000000 !important;
        }
      </style>
    </head>
    <body>
    <table align="center" cellpadding="0" cellspacing="0" width="770px">
      <tr>
        <td>
          <img alt="" height="36" src="https://yastatic.net/s3/passport-static/core/_/C5Z0CrQ7nyH0WIYdoFvbn2NMfyc.png" style="margin-left: 30px; margin-bottom: 15px;" width="68">
          <table align="center" cellpadding="0" cellspacing="0" width="100%%">
            <tr>
              <td>
                <p>Hello, %(firstname)s!</p>

                <p>A phone number has been linked to your Yandex account %(login)s.
                This allows you to restore access to your account using SMS text messages.<br>If you
                linked this number, then everything is okay. If this wasn't you, then it
                could have been someone who gained access to your account.</p>

                <p>If this is the case:</p>

                <ul>
                  <li><a href="https://passport.yandex.com/restoration" target="_blank">
                  restore access</a> to your account</li>

                  <li><a href="https://passport.yandex.com/profile/phones" target="_blank">
                  delete the strange number</a> and, preferrably, replace it with yours</li>
                </ul>

                <p>You can learn more about managing phone numbers linked to your account
                <a href="https://yandex.com/support/passport/authorization/phone.html" target="_blank">
                here</a>.</p>

                <p style="font-family: Arial, sans-serif; color: #000000; font-size: 15px; font-style: italic; margin-top: 30px; margin-bottom: 0;">We care about the safety of your account.<br><br> Sincerely,<br> Yandex ID team</p>
              </td>
            </tr>
          </table>
          <table align="center" cellpadding="0" cellspacing="0" width="100%%">
            <tr>
              <td></td>
            </tr>
            <tr>
              <td>Please do not respond to this message. You can contact Yandex's support service using
              the <a href="https://feedback2.yandex.com/">contact form</a>.</td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    </body>
    </html>
    ''' % {u'login': login, u'firstname': firstname}


def SECURE_PHONE_BOUND_NOTIFICATION_BODY_RUSSIAN(firstname, login):
    return u'''
    <!DOCTYPE html>
    <html>
    <head>
      <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
      <title></title>
      <style>
        .mail-address a,
        .mail-address a[href] {
          text-decoration: none !important;
          color: #000000 !important;
        }
      </style>
    </head>
    <body>
    <table align="center" cellpadding="0" cellspacing="0" width="770px">
      <tr>
        <td>
          <img alt="" height="36" src="https://yastatic.net/s3/passport-static/core/_/7F_vkMrD7zJqJbvEsNzd2YQleQI.png" style="margin-left: 30px; margin-bottom: 15px;" width="68">
          <table align="center" cellpadding="0" cellspacing="0" width="100%%">
            <tr>
              <td>
                <p>Здравствуйте, %(firstname)s!</p>
                <p>К Вашему аккаунту %(login)s на Яндексе привязан номер телефона,
                позволяющий при необходимости восстановить доступ с помощью смс.<br>
                Если номер привязали Вы, то всё в порядке. Если нет — это мог сделать
                злоумышленник.</p>
                <p>В этом случае:</p>
                <ul>
                  <li>
                  <a href="https://passport.yandex.ru/restoration" target="_blank">
                  восстановите доступ</a> к аккаунту;
                  </li>
                  <li>
                  <a href="https://passport.yandex.ru/profile/phones" target="_blank">
                  удалите чужой номер</a> и, желательно, укажите свой.
                  </li>
                </ul>
                <p>
                Узнать больше об управлении привязанными номерами телефонов можно
                <a href="https://yandex.ru/support/passport/authorization/phone.html" target="_blank">
                здесь</a>.
                </p>
                <p>С заботой о безопасности Вашего аккаунта,<br> команда Яндекс ID</p>
              </td>
            </tr>
          </table>
          <table align="center" cellpadding="0" cellspacing="0" width="100%%">
            <tr>
              <td></td>
            </tr>
            <tr>
              <td>Пожалуйста, не отвечайте на это письмо. Связаться со службой поддержки
              Яндекса Вы можете через <a href="https://feedback2.yandex.ru/">
              форму обратной связи</a>.
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    </body>
    </html>
    ''' % {u'login': login, u'firstname': firstname}


def DEALIASIFY_NOTIFICATION_BODY_RUSSIAN(firstname, login, portal_email, alias, alias_email):
    return u'''
    <!doctype html>
    <html>
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title></title>
    <style>
    .mail-address a,
    .mail-address a[href] {
      text-decoration: none !important;
      color: #000000 !important;
    }
    </style>
    </head>
    <body>
    <table cellpadding="0" cellspacing="0" align="center" width="770px">
      <tr>
        <td>
          <img alt="" height="36" src="https://yastatic.net/s3/passport-static/core/_/7F_vkMrD7zJqJbvEsNzd2YQleQI.png" style="margin-left: 30px; margin-bottom: 15px;" width="68">
          <table width="100%%" cellpadding="0" cellspacing="0" align="center">
            <tr>
              <td>
                <p>Здравствуйте, %(firstname)s!</p>
                <p>Вы отказались от использования телефонного номера +%(alias)s в качестве логина.
                По нему больше нельзя войти в Ваш аккаунт.</p>
                <p>Адреса %(formatted_alias_email)s и %(formatted_alias_email_e164)s больше не работают.</p>
                <p>Вы всегда можете включить всё обратно на <a href="https://passport.yandex.ru/profile/phones">
                странице управления привязанными номерами</a>.</p>
                <p>С заботой о безопасности Вашего аккаунта,
                <br> команда Яндекс ID</p>
              </td>
            </tr>
          </table>
          <table width="100%%" cellpadding="0" cellspacing="0" align="center">
            <tr><td></td></tr>
            <tr>
              <td>Пожалуйста, не отвечайте на это письмо. Связаться со службой поддержки Яндекса
              Вы можете через <a href='https://feedback2.yandex.ru/'>форму обратной связи</a>.</td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    </body>
    </html>
    ''' % {
        u'firstname': firstname,
        u'alias': alias,
        u'formatted_alias_email': _format_email(alias_email),
        u'formatted_alias_email_e164': _format_email('+' + alias_email),
    }


def SECURE_PHONE_REMOVAL_STARTED_NOTIFICATION_BODY_ENGLISH(firstname, login):
    return u'''
    <!doctype html>
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <title></title>
        <style>
        .mail-address a,
        .mail-address a[href] {
          text-decoration: none !important;
          color: #000000 !important;
        }
        </style>
    </head>
    <body>
    <table cellpadding="0" cellspacing="0" align="center" width="770px">
      <tr>
        <td>
          <img alt="" height="36" src="https://yastatic.net/s3/passport-static/core/_/C5Z0CrQ7nyH0WIYdoFvbn2NMfyc.png" style="margin-left: 30px; margin-bottom: 15px;" width="68">
          <table width="100%%" cellpadding="0" cellspacing="0" align="center">
            <tr>
              <td>
                <p>Hello, %(firstname)s!</p>

                <p>The main phone number linked to your account %(login)s is marked as
                unavailable.<br>This means that it will be deleted in 14 days. If you made
                this change, then everything is okay. If not, it could have been a hacker.</p>

                <p>In that case:</p>

                <ul>
                  <li>use this number within 14 days to
                  <a href="https://passport.yandex.com/restoration" target="_blank">
                  restore access to the account</a>;</li>

                  <li>click "Cancel" on the
                  <a href="https://passport.yandex.com/profile/phones" target="_blank">
                  phone number management page</a>.<br>If this isn't done, changes will come into
                  effect in 14 days and it will not be possible to use this number
                  to restore access.</li>
                </ul>

                <p>You can learn more about managing phone numbers linked to your account
                <a href="https://yandex.com/support/passport/authorization/phone.html" target="_blank">
                here</a>.</p>

                <p style="font-family: Arial, sans-serif; color: #000000; font-size: 15px; font-style: italic; margin-top: 30px; margin-bottom: 0;">We care about the safety of your account.<br><br> Sincerely,<br> Yandex ID team</p>
              </td>
            </tr>
          </table>
          <table width="100%%" cellpadding="0" cellspacing="0" align="center">
            <tr>
              <td></td>
            </tr>
            <tr>
              <td>Please do not respond to this message. You can contact Yandex's support service using
              the <a href="https://feedback2.yandex.com/">contact form</a>.</td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    </body>
    </html>
    ''' % {
        u'firstname': firstname,
        u'login': login,
    }


def SECURE_PHONE_REMOVAL_STARTED_NOTIFICATION_BODY_RUSSIAN(firstname, login):
    return u'''
    <!doctype html>
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <title></title>
        <style>
        .mail-address a,
        .mail-address a[href] {
          text-decoration: none !important;
          color: #000000 !important;
        }
        </style>
    </head>
    <body>
    <table cellpadding="0" cellspacing="0" align="center" width="770px">
      <tr>
        <td>
          <img alt="" height="36" src="https://yastatic.net/s3/passport-static/core/_/7F_vkMrD7zJqJbvEsNzd2YQleQI.png" style="margin-left: 30px; margin-bottom: 15px;" width="68">
          <table width="100%%" cellpadding="0" cellspacing="0" align="center">
            <tr>
              <td>
                <p>Здравствуйте, %(firstname)s!</p>

                <p>Основной номер телефона, привязанный к вашему аккаунту %(login)s,
                отмечен как недоступный.<br>Это значит, что через 14 дней он будет
                удалён. Если настройку изменили Вы, то всё в порядке. Если нет — это
                мог сделать злоумышленник.</p>

                <p>В таком случае:</p>

                <ul>
                  <li>в течение 14 дней воспользуйтесь этим номером телефона для
                  <a href="https://passport.yandex.ru/restoration" target="_blank">
                  восстановления доступа к аккаунту</a>;</li>

                  <li>нажмите «Отменить» на
                  <a href="https://passport.yandex.ru/profile/phones" target="_blank">
                  странице управления номерами телефонов</a>.<br>Если этого не сделать,
                  через 14 дней изменения вступят в силу и использовать этот номер для
                  восстановления доступа будет невозможно.</li>
                </ul>

                <p>Узнать больше об управлении привязанными номерами телефонов можно
                <a href="https://yandex.ru/support/passport/authorization/phone.html" target="_blank">
                здесь</a>.</p>

                <p>С заботой о безопасности Вашего аккаунта,<br> команда Яндекс ID</p>
              </td>
            </tr>
          </table>
          <table width="100%%" cellpadding="0" cellspacing="0" align="center">
            <tr>
              <td></td>
            </tr>
            <tr>
              <td>Пожалуйста, не отвечайте на это письмо. Связаться со службой поддержки
              Яндекса Вы можете через <a href='https://feedback2.yandex.ru/'>форму
              обратной связи</a>.</td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    </body>
    </html>
    ''' % {
        u'firstname': firstname,
        u'login': login,
    }


def REALIASIFY_NOTIFICATION_BODY_RUSSIAN(firstname, login, portal_email, alias, alias_email):
    return u'''
    <!doctype html>
    <html>
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title></title>
    <style>
    .mail-address a,
    .mail-address a[href] {
      text-decoration: none !important;
      color: #000000 !important;
    }
    </style>
    </head>
    <body>
    <table cellpadding="0" cellspacing="0" align="center" width="770px">
      <tr>
        <td>
          <img alt="" height="36" src="https://yastatic.net/s3/passport-static/core/_/7F_vkMrD7zJqJbvEsNzd2YQleQI.png" style="margin-left: 30px; margin-bottom: 15px;" width="68">
          <table width="100%%" cellpadding="0" cellspacing="0" align="center">
            <tr>
              <td>
                <p>Здравствуйте, %(firstname)s!</p>
                <p>Владелец телефонного номера +%(alias)s привязал его к другому аккаунту на Яндексе. Номер больше нельзя использовать для входа в Ваш аккаунт.</p>
                <p>Адреса %(formatted_alias_email)s и %(formatted_alias_email_e164)s Вам больше не принадлежат.</p>
                <p>Привязать к своему аккаунту новый номер Вы можете в <a href="https://passport.yandex.ru/profile/phones">настройках</a>.</p>
                <p>С заботой о безопасности Вашего аккаунта,<br> команда Яндекс ID</p>
              </td>
            </tr>
          </table>
          <table width="100%%" cellpadding="0" cellspacing="0" align="center">
            <tr>
              <td></td>
            </tr>
            <tr>
              <td>Пожалуйста, не отвечайте на это письмо. Связаться со службой поддержки Яндекса Вы можете через <a href='https://feedback2.yandex.ru/'>форму обратной связи</a>.</td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    </body>
    </html>
    ''' % {
        u'firstname': firstname,
        u'alias': alias,
        u'formatted_alias_email': _format_email(alias_email),
        u'formatted_alias_email_e164': _format_email('+' + alias_email),
    }


ALIASIFY_NOTIFICATION_SUBJECT_RUSSIAN = u'Теперь Вы можете использовать номер телефона как логин'


def _ALIASIFY_NOTIFICATION_BODY(template, firstname, login, portal_email, alias, alias_email):
    formatted_login = u'<span>%s</span>' % login[0]
    if login[1:]:
        formatted_login += u'<span>%s</span>' % login[1:]
    return template % {
        u'firstname': firstname,
        u'formatted_login': formatted_login,
        u'formatted_portal_email': _format_email(portal_email),
        u'_f_ormatted_portal_email': _format_email(portal_email, highlight_first=True),
        u'alias': alias,
        u'formatted_alias_email': _format_email(alias_email),
        u'formatted_alias_email_e164': _format_email('+' + alias_email),
    }


def ALIASIFY_NOTIFICATION_BODY_RUSSIAN(**kwargs):
    template = u'''
       <!doctype html>
       <html>
       <head>
       <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
       <title></title>
       <style>
       .mail-address a,
       .mail-address a[href] {
         text-decoration: none !important;
         color: #000000 !important;
       }
       </style>
       </head>
       <body>
       <table cellpadding="0" cellspacing="0" align="center" width="770px">
         <tr>
           <td>
             <img alt="" height="36" src="https://yastatic.net/s3/passport-static/core/_/7F_vkMrD7zJqJbvEsNzd2YQleQI.png" style="margin-left: 30px; margin-bottom: 15px;" width="68">
             <table width="100%%" cellpadding="0" cellspacing="0" align="center">
               <tr>
                 <td>
                   <p>Здравствуйте, %(firstname)s!</p>
                   <p>Теперь Вы можете входить в Яндекс, указывая в качестве логина свой номер
                   телефона +%(alias)s, и использовать адреса электронной почты
                   %(formatted_alias_email)s и %(formatted_alias_email_e164)s. Письма, отправленные на эти адреса,
                   придут в Ваш ящик на Яндексе.</p>
                   <p>Новые адреса лучше не использовать для регистрации на сайтах: если номер перейдёт
                   к другому человеку, он сможет отвязать его от Вашего аккаунта — и адреса перестанут работать.</p>
                   <p>Вы всегда можете отказаться от использования телефона в качестве логина — это настраивается
                   на <a href="https://passport.yandex.ru/profile/phones">странице управления привязанными
                   номерами</a>.</p>
                   <p>С заботой о безопасности Вашего аккаунта,<br> команда Яндекс ID</p>
                 </td>
               </tr>
             </table>
             <table width="100%%" cellpadding="0" cellspacing="0" align="center">
               <tr><td></td></tr>
               <tr>
                 <td>Пожалуйста, не отвечайте на это письмо. Связаться со службой поддержки Яндекса Вы можете
                 через <a href='https://feedback2.yandex.ru/'>форму обратной связи</a>.</td>
               </tr>
             </table>
           </td>
         </tr>
       </table>
       </body>
       </html>
    '''
    return _ALIASIFY_NOTIFICATION_BODY(template=template, **kwargs)


def SECURE_PHONE_REPLACEMENT_STARTED_NOTIFICATION_BODY_ENGLISH(firstname, login):
    return u'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <title></title>
        <style>
            .mail-address a,
            .mail-address a[href] {
                text-decoration: none !important;
                color: #000000 !important;
            }
            </style>
    </head>
    <body>
    <table align="center" cellpadding="0" cellspacing="0" width="770px">
      <tr>
        <td>
          <img alt="" height="36" src="https://yastatic.net/s3/passport-static/core/_/C5Z0CrQ7nyH0WIYdoFvbn2NMfyc.png" style="margin-left: 30px; margin-bottom: 15px;" width="68">

          <table align="center" cellpadding="0" cellspacing="0" width="100%%">
            <tr>
              <td>
                <p>Hello, %(firstname)s!</p>

                <p>The main phone number linked to your account %(login)s was changed.
                If you made this change, then everything is okay. If not, it could have
                been a hacker.</p>

                <p>In that case:</p>

                <ul>
                  <li>use this number within 14 days to
                  <a href="https://passport.yandex.com/restoration" target="_blank">
                  restore access to the account</a>;</li>

                  <li>cancel the change on the <a href="https://passport.yandex.com/profile/phones" target="_blank">
                  phone number management page</a>.<br>If this isn't done, the new number will go into effect in 14 days,
                  and it will then become impossible to use the old number to restore access to your account.</li>
                </ul>

                <p>You can learn more about managing phone numbers linked to your account
                <a href="https://yandex.com/support/passport/authorization/phone.html" target="_blank">
                here</a>.</p>

                <p style="font-family: Arial, sans-serif; color: #000000; font-size: 15px; font-style: italic; margin-top: 30px; margin-bottom: 0;">We care about the safety of your account.<br><br> Sincerely,<br> Yandex ID team</p>
              </td>
            </tr>
          </table>
          <table align="center" cellpadding="0" cellspacing="0" width="100%%">
            <tr><td></td></tr>
            <tr>
              <td>Please do not respond to this message. You can contact Yandex's support service using
              the <a href="https://feedback2.yandex.com/">contact form</a>.</td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    </body>
    </html>
    ''' % {
        'firstname': firstname,
        'login': login,
    }


def SECURE_PHONE_REPLACEMENT_STARTED_NOTIFICATION_BODY_RUSSIAN(firstname, login):
    return u'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <title></title>
        <style>
            .mail-address a,
            .mail-address a[href] {
                text-decoration: none !important;
                color: #000000 !important;
            }
            </style>
    </head>
    <body>
    <table align="center" cellpadding="0" cellspacing="0" width="770px">
      <tr>
        <td>
          <img alt="" height="36" src="https://yastatic.net/s3/passport-static/core/_/7F_vkMrD7zJqJbvEsNzd2YQleQI.png" style="margin-left: 30px; margin-bottom: 15px;" width="68">

          <table align="center" cellpadding="0" cellspacing="0" width="100%%">
            <tr>
              <td>
                <p>Здравствуйте, %(firstname)s!</p>

                <p>Изменён основной номер телефона, привязанный к вашему аккаунту %(login)s.
                Если номер изменили Вы, то всё в порядке. Если нет — это мог сделать
                злоумышленник.</p>

                <p>В таком случае:</p>

                <ul>
                  <li>в течение 14 дней воспользуйтесь этим номером телефона для
                  <a href="https://passport.yandex.ru/restoration" target="_blank">
                  восстановления доступа к аккаунту</a>;</li>

                  <li>отмените изменение на
                  <a href="https://passport.yandex.ru/profile/phones" target="_blank">
                  странице управления номерами телефонов</a>. <br>Если этого не сделать,
                  через 14 дней изменения вступят в силу, и использовать этот номер для
                  восстановления доступа будет невозможно.</li>
                </ul>
                <p>Узнать больше об управлении привязанными номерами телефонов можно
                <a href="https://yandex.ru/support/passport/authorization/phone.html" target="_blank">
                здесь</a>.</p>
                <p>С заботой о безопасности Вашего аккаунта,<br> команда Яндекс ID</p>
              </td>
            </tr>
          </table>
          <table align="center" cellpadding="0" cellspacing="0" width="100%%">
            <tr><td></td></tr>
            <tr>
              <td>Пожалуйста, не отвечайте на это письмо. Связаться со службой поддержки
              Яндекса Вы можете через <a href="https://feedback2.yandex.ru/">
              форму обратной связи</a>.</td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    </body>
    </html>
    ''' % {
        'firstname': firstname,
        'login': login,
    }


def SECURE_PHONE_REPLACED_NOTIFICATION_BODY_ENGLISH(firstname, login):
    return u'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <title></title>
        <style>
            .mail-address a,
            .mail-address a[href] {
                text-decoration: none !important;
                color: #000000 !important;
            }
            </style>
    </head>
    <body>
    <table align="center" cellpadding="0" cellspacing="0" width="770px">
      <tr>
        <td>
          <img alt="" height="36" src="https://yastatic.net/s3/passport-static/core/_/C5Z0CrQ7nyH0WIYdoFvbn2NMfyc.png" style="margin-left: 30px; margin-bottom: 15px;" width="68">

          <table align="center" cellpadding="0" cellspacing="0" width="100%%">
            <tr>
              <td>
                <p>Hello, %(firstname)s!</p>

                <p>The main phone number linked to your account %(login)s has
                been changed.</p>

                <p>You can learn more about managing phone numbers linked to your account
                <a href="https://yandex.com/support/passport/authorization/phone.html" target="_blank">
                here</a>.</p>

                <p style="font-family: Arial, sans-serif; color: #000000; font-size: 15px; font-style: italic; margin-top: 30px; margin-bottom: 0;">We care about the safety of your account.<br><br> Sincerely,<br> Yandex ID team</p>
              </td>
            </tr>
          </table>
          <table align="center" cellpadding="0" cellspacing="0" width="100%%">
            <tr><td></td></tr>
            <tr>
              <td>Please do not respond to this message. You can contact Yandex's support service using
              the <a href="https://feedback2.yandex.com/">contact form</a>.</td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    </body>
    </html>
    ''' % {
        'firstname': firstname,
        'login': login,
    }


def SECURE_PHONE_REPLACED_NOTIFICATION_BODY_RUSSIAN(firstname, login):
    return u'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <title></title>
        <style>
            .mail-address a,
            .mail-address a[href] {
                text-decoration: none !important;
                color: #000000 !important;
            }
            </style>
    </head>
    <body>
    <table align="center" cellpadding="0" cellspacing="0" width="770px">
      <tr>
        <td>
          <img alt="" height="36" src="https://yastatic.net/s3/passport-static/core/_/7F_vkMrD7zJqJbvEsNzd2YQleQI.png" style="margin-left: 30px; margin-bottom: 15px;" width="68">

          <table align="center" cellpadding="0" cellspacing="0" width="100%%">
            <tr>
              <td>
                <p>Здравствуйте, %(firstname)s!</p>

                <p>Изменён основной номер телефона, привязанный к Вашему аккаунту %(login)s.</p>

                <p>Узнать больше об управлении привязанными номерами телефонов можно
                <a href="https://yandex.ru/support/passport/authorization/phone.html" target="_blank">
                здесь</a>.</p>
                <p>С заботой о безопасности Вашего аккаунта,<br> команда Яндекс ID</p>
              </td>
            </tr>
          </table>
          <table align="center" cellpadding="0" cellspacing="0" width="100%%">
            <tr><td></td></tr>
            <tr>
              <td>Пожалуйста, не отвечайте на это письмо. Связаться со службой поддержки
              Яндекса Вы можете через <a href="https://feedback2.yandex.ru/">
              форму обратной связи</a>.</td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    </body>
    </html>
    ''' % {
        'firstname': firstname,
        'login': login,
    }


def SECURE_PHONE_REMOVED_WITH_QUARANTINE_NOTIFICATION_BODY_RUSSIAN(firstname, login):
    return u'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <title></title>
        <style>
            .mail-address a,
            .mail-address a[href] {
                text-decoration: none !important;
                color: #000000 !important;
            }
            </style>
    </head>
    <body>
    <table align="center" cellpadding="0" cellspacing="0" width="770px">
      <tr>
        <td>
          <img alt="" height="36" src="https://yastatic.net/s3/passport-static/core/_/7F_vkMrD7zJqJbvEsNzd2YQleQI.png" style="margin-left: 30px; margin-bottom: 15px;" width="68">

          <table align="center" cellpadding="0" cellspacing="0" width="100%%">
            <tr>
              <td>
                <p>Здравствуйте, %(firstname)s!</p>

                <p>Основной номер телефона, который был привязан к Вашему аккаунту %(login)s
                удалён. Это произошло потому, что 14 дней назад номер был отмечен как недоступный.
                Теперь его нельзя использовать для восстановления доступа.<br>Зато можно
                <a href="https://passport.yandex.ru/profile/phones" target="_blank">
                привязать к аккаунту новый основной номер</a>.</p>

                <p>Узнать больше об управлении привязанными номерами телефонов можно
                <a href="https://yandex.ru/support/passport/authorization/phone.html" target="_blank">
                здесь</a>.</p>

                <p>С заботой о безопасности Вашего аккаунта,<br> команда Яндекс ID</p>
              </td>
            </tr>
          </table>
          <table align="center" cellpadding="0" cellspacing="0" width="100%%">
            <tr><td></td></tr>
            <tr>
              <td>Пожалуйста, не отвечайте на это письмо. Связаться со службой поддержки
              Яндекса Вы можете через <a href="https://feedback2.yandex.ru/">
              форму обратной связи</a>.</td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    </body>
    </html>
    ''' % {
        'firstname': firstname,
        'login': login,
    }


def SECURE_PHONE_REMOVED_WITHOUT_QUARANTINE_NOTIFICATION_BODY_ENGLISH(firstname, login):
    return u'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <title></title>
        <style>
            .mail-address a,
            .mail-address a[href] {
                text-decoration: none !important;
                color: #000000 !important;
            }
            </style>
    </head>
    <body>
    <table align="center" cellpadding="0" cellspacing="0" width="770px">
      <tr>
        <td>
          <img alt="" height="36" src="https://yastatic.net/s3/passport-static/core/_/C5Z0CrQ7nyH0WIYdoFvbn2NMfyc.png" style="margin-left: 30px; margin-bottom: 15px;" width="68">

          <table align="center" cellpadding="0" cellspacing="0" width="100%%">
            <tr>
              <td>
                <p>Hello, %(firstname)s!</p>

                <p>The main phone number linked to your account %(login)s has been deleted. If you
                deleted this number, then everything is okay. If this wasn't you, then it
                could have been someone who gained unauthorized access to your account.</p>

                <p>In that case:</p>

                <ul>
                  <li><a href="https://passport.yandex.com/profile/password" target="_blank">
                  change the password</a>;</li>

                  <li>if you are unable to change your password, you can still
                  <a href="https://passport.yandex.com/restoration" target="_blank">
                  restore access</a> to your account;</li>

                  <li><a href="https://passport.yandex.com/profile/phones" target="_blank">
                  restore the deleted number</a>.</li>
                </ul>

                <p>You can learn more about managing phone numbers linked to your account
                <a href="https://yandex.com/support/passport/authorization/phone.html" target="_blank">
                here</a>.</p>

                <p style="font-family: Arial, sans-serif; color: #000000; font-size: 15px; font-style: italic; margin-top: 30px; margin-bottom: 0;">We care about the safety of your account.<br><br> Sincerely,<br> Yandex ID team</p>
              </td>
            </tr>
          </table>
          <table align="center" cellpadding="0" cellspacing="0" width="100%%">
            <tr><td></td></tr>
            <tr>
              <td>Please do not respond to this message. You can contact Yandex's support service using
              the <a href="https://feedback2.yandex.com/">contact form</a>.</td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    </body>
    </html>
    ''' % {
        'firstname': firstname,
        'login': login,
    }


def SECURE_PHONE_REMOVED_WITHOUT_QUARANTINE_NOTIFICATION_BODY_RUSSIAN(firstname, login):
    return u'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <title></title>
        <style>
            .mail-address a,
            .mail-address a[href] {
                text-decoration: none !important;
                color: #000000 !important;
            }
            </style>
    </head>
    <body>
    <table align="center" cellpadding="0" cellspacing="0" width="770px">
      <tr>
        <td>
          <img alt="" height="36" src="https://yastatic.net/s3/passport-static/core/_/7F_vkMrD7zJqJbvEsNzd2YQleQI.png" style="margin-left: 30px; margin-bottom: 15px;" width="68">

          <table align="center" cellpadding="0" cellspacing="0" width="100%%">
            <tr>
              <td>
                <p>Здравствуйте, %(firstname)s!</p>

                <p>Удален основной номер телефона, привязанный к вашему аккаунту %(login)s.
                Если номер удалили Вы, то всё в порядке. Если нет — это мог сделать
                злоумышленник.</p>

                <p>В таком случае:</p>

                <ul>
                  <li><a href="https://passport.yandex.ru/profile/password" target="_blank">
                  смените пароль</a>;</li>

                  <li>если пароль сменить не получается,
                  <a href="https://passport.yandex.ru/restoration" target="_blank">
                  восстановите доступ</a> к аккаунту;</li>

                  <li><a href="https://passport.yandex.ru/profile/phones" target="_blank">
                  верните удаленный номер</a>
                  обратно.</li>
                </ul>

                <p>Узнать больше об управлении привязанными номерами телефонов можно
                <a href="https://yandex.ru/support/passport/authorization/phone.html" target="_blank">
                здесь</a>.</p>

                <p>С заботой о безопасности Вашего аккаунта,<br> команда Яндекс ID</p>
              </td>
            </tr>
          </table>
          <table align="center" cellpadding="0" cellspacing="0" width="100%%">
            <tr><td></td></tr>
            <tr>
              <td>Пожалуйста, не отвечайте на это письмо. Связаться со службой поддержки
              Яндекса Вы можете через <a href="https://feedback2.yandex.ru/">
              форму обратной связи</a>.</td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
    </body>
    </html>
    ''' % {
        'firstname': firstname,
        'login': login,
    }


def _format_email(email, highlight_first=False):
    mailbox, hostname = email.split(u'@')
    hostname = u'<span>.</span>'.join(hostname.split(u'.'))
    if highlight_first and len(mailbox) > 1:
        mailbox = u'<span>%s</span><span>%s</span>' % (mailbox[0], mailbox[1:])
    else:
        mailbox = u'<span>%s</span>' % mailbox
    return u'%s@%s' % (mailbox, hostname)


def assert_user_notified_about_aliasify(mailer_faker, language, email_address,
                                        firstname, login, portal_email,
                                        phonenumber_alias):
    if language == u'en':
        raise NotImplementedError()  # pragma: no cover
    else:
        subject = ALIASIFY_NOTIFICATION_SUBJECT_RUSSIAN
        body = ALIASIFY_NOTIFICATION_BODY_RUSSIAN

    body = body(
        firstname=firstname,
        login=login,
        portal_email=portal_email,
        alias=phonenumber_alias,
        alias_email=phonenumber_alias + u'@' + portal_email.split(u'@')[1],
    )

    assert_email_message_sent(mailer_faker, email_address, subject, body)


def assert_user_notified_about_realiasify(mailer_faker, language,
                                          email_address, firstname, login,
                                          portal_email, phonenumber_alias):
    if language == u'en':
        raise NotImplementedError()  # pragma: no cover
    else:
        subject = REALIASIFY_NOTIFICATION_SUBJECT_RUSSIAN
        body = REALIASIFY_NOTIFICATION_BODY_RUSSIAN

    subject = subject(alias='+' + phonenumber_alias)

    body = body(
        firstname=firstname,
        login=login,
        portal_email=portal_email,
        alias=phonenumber_alias,
        alias_email=phonenumber_alias + u'@' + portal_email.split(u'@')[1],
    )

    assert_email_message_sent(mailer_faker, email_address, subject, body)


def assert_user_notified_about_dealiasify(mailer_faker, language,
                                          email_address, firstname, login,
                                          portal_email, phonenumber_alias):
    if language == u'en':
        raise NotImplementedError()  # pragma: no cover
    else:
        subject = DEALIASIFY_NOTIFICATION_SUBJECT_RUSSIAN
        body = DEALIASIFY_NOTIFICATION_BODY_RUSSIAN

    body = body(
        firstname=firstname,
        login=login,
        portal_email=portal_email,
        alias=phonenumber_alias,
        alias_email=phonenumber_alias + u'@' + portal_email.split(u'@')[1],
    )

    assert_email_message_sent(mailer_faker, email_address, subject, body)


def assert_user_notified_about_secure_phone_bound(mailer_faker, language,
                                                  email_address, firstname, login):
    if language == 'ru':
        subject = SECURE_PHONE_BOUND_NOTIFICATION_SUBJECT_RUSSIAN
        body = SECURE_PHONE_BOUND_NOTIFICATION_BODY_RUSSIAN
    elif language == 'en':
        subject = SECURE_PHONE_BOUND_NOTIFICATION_SUBJECT_ENGLISH
        body = SECURE_PHONE_BOUND_NOTIFICATION_BODY_ENGLISH
    else:
        raise NotImplementedError(language)

    body = body(
        firstname=firstname,
        login=login,
    )
    assert_email_message_sent(mailer_faker, email_address, subject, body)


def assert_user_notified_about_secure_phone_removal_started(mailer_faker, language,
                                                            email_address, firstname, login):
    if language == 'ru':
        subject = SECURE_PHONE_REMOVAL_STARTED_NOTIFICATION_SUBJECT_RUSSIAN
        body = SECURE_PHONE_REMOVAL_STARTED_NOTIFICATION_BODY_RUSSIAN
    elif language == 'en':
        subject = SECURE_PHONE_REMOVAL_STARTED_NOTIFICATION_SUBJECT_ENGLISH
        body = SECURE_PHONE_REMOVAL_STARTED_NOTIFICATION_BODY_ENGLISH
    else:
        raise NotImplementedError(language)

    body = body(firstname=firstname, login=login)
    assert_email_message_sent(mailer_faker, email_address, subject, body)


def assert_user_notified_about_secure_phone_removed_with_quarantine(mailer_faker, language,
                                                                    email_address, firstname, login):
    if language == 'ru':
        subject = SECURE_PHONE_REMOVED_WITH_QUARANTINE_NOTIFICATION_SUBJECT_RUSSIAN
        body = SECURE_PHONE_REMOVED_WITH_QUARANTINE_NOTIFICATION_BODY_RUSSIAN
    else:
        raise NotImplementedError(language)

    body = body(firstname=firstname, login=login)
    assert_email_message_sent(mailer_faker, email_address, subject, body)


def assert_user_notified_about_secure_phone_removed_without_quarantine(mailer_faker, language,
                                                                       email_address, firstname, login):
    if language == 'ru':
        subject = SECURE_PHONE_REMOVED_WITHOUT_QUARANTINE_NOTIFICATION_SUBJECT_RUSSIAN
        body = SECURE_PHONE_REMOVED_WITHOUT_QUARANTINE_NOTIFICATION_BODY_RUSSIAN
    elif language == 'en':
        subject = SECURE_PHONE_REMOVED_WITHOUT_QUARANTINE_NOTIFICATION_SUBJECT_ENGLISH
        body = SECURE_PHONE_REMOVED_WITHOUT_QUARANTINE_NOTIFICATION_BODY_ENGLISH
    else:
        raise NotImplementedError(language)

    body = body(firstname=firstname, login=login)
    assert_email_message_sent(mailer_faker, email_address, subject, body)


def assert_user_notified_about_secure_phone_replacement_started(mailer_faker, language,
                                                                email_address, firstname, login):
    if language == 'ru':
        subject = SECURE_PHONE_REPLACEMENT_STARTED_NOTIFICATION_SUBJECT_RUSSIAN
        body = SECURE_PHONE_REPLACEMENT_STARTED_NOTIFICATION_BODY_RUSSIAN
    elif language == 'en':
        subject = SECURE_PHONE_REPLACEMENT_STARTED_NOTIFICATION_SUBJECT_ENGLISH
        body = SECURE_PHONE_REPLACEMENT_STARTED_NOTIFICATION_BODY_ENGLISH
    else:
        raise NotImplementedError(language)

    body = body(firstname=firstname, login=login)
    assert_email_message_sent(mailer_faker, email_address, subject, body)


def assert_user_notified_about_secure_phone_replaced(mailer_faker, language,
                                                     email_address, firstname, login):
    if language == 'ru':
        subject = SECURE_PHONE_REPLACED_SUBJECT_RUSSIAN
        body = SECURE_PHONE_REPLACED_NOTIFICATION_BODY_RUSSIAN
    elif language == 'en':
        subject = SECURE_PHONE_REPLACED_SUBJECT_ENGLISH
        body = SECURE_PHONE_REPLACED_NOTIFICATION_BODY_ENGLISH
    else:
        raise NotImplementedError(language)

    body = body(firstname=firstname, login=login)
    assert_email_message_sent(mailer_faker, email_address, subject, body)
