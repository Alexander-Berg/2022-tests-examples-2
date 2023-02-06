import { render, screen } from '@testing-library/react'
import { RecoilRoot } from 'recoil'

import { PageEnvProvider } from 'client/lib/page-env'
import { I18nContext } from 'i18n/provider/I18nContext'
import { PageEnv } from 'lib/page-env'

import { DeliveryConditionsModal } from './DeliveryConditionsModal'

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const i18n = { common: () => 'close' } as any

describe('render delivery conditions modal', () => {
  test('Should render all passed props as text after first render', () => {
    const pageEnv: PageEnv = {
      hostname: 'lavka.yandex.ru',
      origin: 'https://lavka.yandex.ru',
      lavkaHost: 'yandex',
      locale: {
        lang: 'ru',
        region: 'RU',
      },
      url: '/',
      fullUrl: '/',
      isFallbackLang: true,
      isFallbackRegion: true,
      isDeliYandex: false,
    }
    render(
      <PageEnvProvider pageEnv={pageEnv}>
        <RecoilRoot>
          <I18nContext.Provider value={{ i18n, i18nRaw: i18n }}>
            <DeliveryConditionsModal
              isOpen
              title="title"
              description="description"
              deliveryInfoItems={[{ title: 'info item title', description: 'info item description' }]}
              subTitle="subTitle"
              subDescription="subDescription"
              confirmButtonText="confirmButtonText"
              detailsDescription="detailsDescription"
              detailsTitle="detailsTitle"
              onClose={() => true}
            />
          </I18nContext.Provider>
        </RecoilRoot>
      </PageEnvProvider>,
    )

    expect(screen.getByText('title')).toBeTruthy()
    expect(screen.getByText('description')).toBeTruthy()
    expect(screen.getByText('subTitle')).toBeTruthy()
    expect(screen.getByText('subDescription')).toBeTruthy()
    expect(screen.getByText('confirmButtonText')).toBeTruthy()
    expect(screen.getByText('detailsDescription')).toBeTruthy()
    expect(screen.getByText('detailsTitle')).toBeTruthy()
    expect(screen.getByText('info item title')).toBeTruthy()
    expect(screen.getByText('info item description')).toBeTruthy()
  })
})
