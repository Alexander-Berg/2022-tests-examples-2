import type { OpenPageOptions } from '@lavka/tests'
import { BaseMobilePage } from '@lavka/tests'

export class MobilePage extends BaseMobilePage {
  async open(path: string, options?: OpenPageOptions) {
    await this.setInnerWindowSize(375, 812)
    await this.browser.openPage(path, {
      ...options,
      cookies: { ...options?.cookies, hideDevtools: 'true', isPhone: 'true' },
    })
  }
}
