import {ComponentType} from 'react'
import {QueryClient, QueryClientProvider} from 'react-query'

import {I18nProvider, initializeI18nApi, prepareI18n} from '@lavka/i18n'
import {
  ALERT_MODAL_ID,
  CONFIRM_MODAL_ID,
  createTestStore,
  IStore,
  ModalsInjector,
  StoreProvider,
  useRegisterModal,
} from '@lavka/store'
import {TestConfirmModal, TestAlertModal} from '@lavka/store/tests'

import {createTestQueryClient} from '../client/create-test-query-client'

const ModalsRegistrator = () => {
  useRegisterModal({
    id: CONFIRM_MODAL_ID,
    type: 'modal',
    ModalComponent: TestConfirmModal,
    props: {},
  })

  useRegisterModal({
    id: ALERT_MODAL_ID,
    type: 'modal',
    ModalComponent: TestAlertModal,
    props: {},
  })

  return null
}

interface TestWrapperOptions {
  store?: IStore
  queryClient?: QueryClient
}

export const createTestWrapper = ({store, queryClient}: TestWrapperOptions): ComponentType => {
  const finalStore = store ?? createTestStore()
  const finalQueryClient = queryClient ?? createTestQueryClient()

  const i18nData = prepareI18n(
    {ru: {}, en: {}, he: {}, fr: {}},
    {
      app: 'superapp',
      lang: 'ru',
      brand: 'lavka',
    },
  )

  const i18nAPI = initializeI18nApi(
    {
      lang: 'ru',
      isProduction: false,
      logger: console,
      brand: 'lavka',
    },
    i18nData,
  )

  return ({children}) => {
    return (
      <I18nProvider api={i18nAPI}>
        <StoreProvider store={finalStore}>
          <QueryClientProvider client={finalQueryClient}>
            <ModalsRegistrator />
            <ModalsInjector />
            {children}
          </QueryClientProvider>
        </StoreProvider>
      </I18nProvider>
    )
  }
}
