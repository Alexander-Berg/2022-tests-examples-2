import {calcCashbackState} from '.'

const NO_BANNER_STATE = {
  SHOW_BANNER: false,
  SHOW_LOGIN_POPUP: false,
  SHOW_OPT_IN_POPUP: false,
  SHOW_PLUS_HOME_POPUP: false,
}

const WITH_LOGGIN_BANNER_STATE = {
  SHOW_BANNER: true,
  SHOW_LOGIN_POPUP: true,
  SHOW_OPT_IN_POPUP: false,
  SHOW_PLUS_HOME_POPUP: false,
}

const WITH_OPT_IN_BANNER_STATE = {
  SHOW_BANNER: true,
  SHOW_LOGIN_POPUP: false,
  SHOW_OPT_IN_POPUP: true,
  SHOW_PLUS_HOME_POPUP: false,
}

const WITH_PLUS_HOME_BANNER_STATE = {
  SHOW_BANNER: true,
  SHOW_LOGIN_POPUP: false,
  SHOW_OPT_IN_POPUP: false,
  SHOW_PLUS_HOME_POPUP: true,
}

describe('Состояния кэшбека плюса', () => {
  describe('Веб', () => {
    commonCases(false)

    describe('Есть эксперимент плюса, но нет флага requiresOptIn', () => {
      it('Если нет эксперимента паспорта -- не показываем баннер', () => {
        expect(
          calcCashbackState({
            plusExpEnabled: true,
            plusExpReqOptIn: false,
            passportExpEnabled: false,
            trustExpEnabled: true,
            isSuperApp: false,
            isSuperAppTrustSupported: false,
            isMagnitApp: false,
            isUserLoggedIn: false,
            yandexPlusCashbackOptInChecked: false,
          }),
        ).toEqual(NO_BANNER_STATE)
      })

      it('Если нет эксперимента траста -- не показываем баннер', () => {
        expect(
          calcCashbackState({
            plusExpEnabled: true,
            plusExpReqOptIn: false,
            passportExpEnabled: true,
            trustExpEnabled: false,
            isSuperApp: false,
            isSuperAppTrustSupported: false,
            isMagnitApp: false,
            isUserLoggedIn: false,
            yandexPlusCashbackOptInChecked: false,
          }),
        ).toEqual(NO_BANNER_STATE)
      })

      it('Если нет экспериментов и траста, и паспорта -- не показываем баннер', () => {
        expect(
          calcCashbackState({
            plusExpEnabled: true,
            plusExpReqOptIn: false,
            passportExpEnabled: false,
            trustExpEnabled: false,
            isSuperApp: false,
            isSuperAppTrustSupported: false,
            isMagnitApp: false,
            isUserLoggedIn: false,
            yandexPlusCashbackOptInChecked: false,
          }),
        ).toEqual(NO_BANNER_STATE)
      })

      describe('Если есть все эксперименты', () => {
        it('Если пользователь не авторизован -- показываем баннер-логинилку', () => {
          expect(
            calcCashbackState({
              plusExpEnabled: true,
              plusExpReqOptIn: false,
              passportExpEnabled: true,
              isUserLoggedIn: false,
              trustExpEnabled: true,
              isSuperApp: false,
              isSuperAppTrustSupported: false,
              isMagnitApp: false,
              yandexPlusCashbackOptInChecked: false,
            }),
          ).toEqual(WITH_LOGGIN_BANNER_STATE)
        })

        it('Если пользователь авторизован -- показываем баннер, открывающий дом плюса', () => {
          expect(
            calcCashbackState({
              plusExpEnabled: true,
              plusExpReqOptIn: false,
              passportExpEnabled: true,
              isUserLoggedIn: true,
              trustExpEnabled: true,
              isSuperApp: false,
              isSuperAppTrustSupported: false,
              isMagnitApp: false,
              yandexPlusCashbackOptInChecked: false,
            }),
          ).toEqual(WITH_PLUS_HOME_BANNER_STATE)
        })
      })
    })
  })

  describe('СуперАпп', () => {
    commonCases(true)

    describe('Есть эксперимент плюса, но нет флага requiresOptIn', () => {
      describe('Если нет эксперимента паспорта', () => {
        it('если пользователь не залогинен -- показываем баннер-логинилку', () => {
          expect(
            calcCashbackState({
              plusExpEnabled: true,
              plusExpReqOptIn: false,
              isUserLoggedIn: false,
              passportExpEnabled: false,
              trustExpEnabled: true,
              isSuperApp: true,
              isSuperAppTrustSupported: true,
              isMagnitApp: false,
              yandexPlusCashbackOptInChecked: false,
            }),
          ).toEqual(WITH_LOGGIN_BANNER_STATE)
        })

        it('если пользователь залогинен -- показываем баннер, открывающий дом плюса', () => {
          expect(
            calcCashbackState({
              plusExpEnabled: true,
              plusExpReqOptIn: false,
              isUserLoggedIn: true,
              passportExpEnabled: false,
              trustExpEnabled: true,
              isSuperApp: true,
              isSuperAppTrustSupported: true,
              isMagnitApp: false,
              yandexPlusCashbackOptInChecked: false,
            }),
          ).toEqual(WITH_PLUS_HOME_BANNER_STATE)
        })
      })

      it('Если нет эксперимента траста -- не показываем баннер', () => {
        expect(
          calcCashbackState({
            plusExpEnabled: true,
            plusExpReqOptIn: false,
            passportExpEnabled: true,
            trustExpEnabled: false,
            isSuperApp: true,
            isSuperAppTrustSupported: true,
            isMagnitApp: false,
            yandexPlusCashbackOptInChecked: false,
            isUserLoggedIn: false,
          }),
        ).toEqual(NO_BANNER_STATE)
      })

      it('Если нет экспериментов и траста, и паспорта -- не показываем баннер', () => {
        expect(
          calcCashbackState({
            plusExpEnabled: true,
            plusExpReqOptIn: false,
            passportExpEnabled: false,
            trustExpEnabled: false,
            isSuperApp: true,
            isSuperAppTrustSupported: true,
            isMagnitApp: false,
            yandexPlusCashbackOptInChecked: false,
            isUserLoggedIn: false,
          }),
        ).toEqual(NO_BANNER_STATE)
      })

      describe('Если есть все эксперименты', () => {
        it('Если пользователь не авторизован -- показываем баннер-логинилку', () => {
          expect(
            calcCashbackState({
              plusExpEnabled: true,
              plusExpReqOptIn: false,
              passportExpEnabled: true,
              isUserLoggedIn: false,
              trustExpEnabled: true,
              isSuperApp: true,
              isSuperAppTrustSupported: true,
              isMagnitApp: false,
              yandexPlusCashbackOptInChecked: false,
            }),
          ).toEqual(WITH_LOGGIN_BANNER_STATE)
        })

        it('Если пользователь авторизован -- показываем баннер, открывающий дом плюса', () => {
          expect(
            calcCashbackState({
              plusExpEnabled: true,
              plusExpReqOptIn: false,
              passportExpEnabled: true,
              isUserLoggedIn: true,
              trustExpEnabled: true,
              isSuperApp: true,
              isSuperAppTrustSupported: true,
              isMagnitApp: false,
              yandexPlusCashbackOptInChecked: false,
            }),
          ).toEqual(WITH_PLUS_HOME_BANNER_STATE)
        })
      })
    })
  })
})

function commonCases(isSuperApp: boolean) {
  it('Нет эксперимента плюса -- не показываем баннер', () => {
    expect(
      calcCashbackState({
        plusExpEnabled: false,
        isSuperApp,
        plusExpReqOptIn: false,
        passportExpEnabled: false,
        trustExpEnabled: false,
        isSuperAppTrustSupported: true,
        isMagnitApp: false,
        isUserLoggedIn: false,
        yandexPlusCashbackOptInChecked: false,
      }),
    ).toEqual(NO_BANNER_STATE)
  })

  describe('Есть эксперимент плюса c флагом requiresOptIn', () => {
    it('Если нет эксперимента паспорта -- показываем баннер', () => {
      expect(
        calcCashbackState({
          plusExpEnabled: true,
          plusExpReqOptIn: true,
          passportExpEnabled: false,
          isSuperApp,
          trustExpEnabled: true,
          isSuperAppTrustSupported: true,
          isMagnitApp: false,
          isUserLoggedIn: false,
          yandexPlusCashbackOptInChecked: false,
        }),
      ).toMatchObject({
        SHOW_BANNER: true,
      })
    })

    it('Если нет эксперимента траста -- показываем баннер', () => {
      expect(
        calcCashbackState({
          plusExpEnabled: true,
          plusExpReqOptIn: true,
          trustExpEnabled: false,
          isSuperApp,
          isSuperAppTrustSupported: true,
          isMagnitApp: false,
          isUserLoggedIn: false,
          yandexPlusCashbackOptInChecked: false,
          passportExpEnabled: false,
        }),
      ).toMatchObject({
        SHOW_BANNER: true,
      })
    })

    it('Если нет экспериментов и траста, и паспорта -- показываем баннер', () => {
      expect(
        calcCashbackState({
          plusExpEnabled: true,
          plusExpReqOptIn: true,
          passportExpEnabled: false,
          trustExpEnabled: false,
          isSuperApp,
          isSuperAppTrustSupported: true,
          isMagnitApp: false,
          isUserLoggedIn: false,
          yandexPlusCashbackOptInChecked: false,
        }),
      ).toMatchObject({
        SHOW_BANNER: true,
      })
    })

    it('Если пользователь не авторизован -- показываем баннер-логинилку', () => {
      expect(
        calcCashbackState({
          plusExpEnabled: true,
          plusExpReqOptIn: true,
          isUserLoggedIn: false,
          isSuperApp,
          passportExpEnabled: false,
          trustExpEnabled: false,
          isSuperAppTrustSupported: true,
          isMagnitApp: false,
          yandexPlusCashbackOptInChecked: false,
        }),
      ).toEqual(WITH_LOGGIN_BANNER_STATE)
    })

    describe('Если пользователь авторизован', () => {
      it('Если пользователь ещё не подтверждал opt-in (локальная переменная yandexPlusCashbackOptInChecked не проставлена) -- показываем окно с подтверждением opt-in', () => {
        expect(
          calcCashbackState({
            plusExpEnabled: true,
            plusExpReqOptIn: true,
            isUserLoggedIn: true,
            yandexPlusCashbackOptInChecked: false,
            isSuperApp,
            passportExpEnabled: false,
            trustExpEnabled: false,
            isSuperAppTrustSupported: true,
            isMagnitApp: false,
          }),
        ).toEqual(WITH_OPT_IN_BANNER_STATE)
      })

      it('Если пользователь уже подтверждал opt-in (локальная переменная yandexPlusCashbackOptInChecked проставлена) -- показываем окно дома плюса', () => {
        expect(
          calcCashbackState({
            plusExpEnabled: true,
            plusExpReqOptIn: true,
            isUserLoggedIn: true,
            yandexPlusCashbackOptInChecked: true,
            isSuperApp,
            passportExpEnabled: false,
            trustExpEnabled: false,
            isSuperAppTrustSupported: true,
            isMagnitApp: false,
          }),
        ).toEqual(WITH_PLUS_HOME_BANNER_STATE)
      })
    })
  })
}
