describe('BankCard', function () {
  const elements = {
    component: "[data-testid='element']",
  };

  describe('Default', function () {
    it('base', async function () {
      const { browser } = this;

      await browser.yaOpenStory('bank-card', 'default', {
        args: 'bank:atb;paymentSystem:jcb;cardNumber:•• 4100',
      });

      await browser.assertView('default', elements.component);
    });

    it('hovered', async function () {
      const { browser } = this;

      await browser.yaOpenStory('bank-card', 'default', {
        args: 'bank:atb;paymentSystem:jcb;cardNumber:•• 4100',
      });
      const bankCard = await browser.$(elements.component);

      await bankCard.moveTo();

      await browser.assertView('default-hover', elements.component);
    });

    it('withLabel', async function () {
      const { browser } = this;

      await browser.yaOpenStory('bank-card', 'default', {
        args: 'bank:atb;paymentSystem:jcb;cardNumber:•• 4100;label:label',
      });

      await browser.assertView('default-label', elements.component);
    });

    it('withMoney', async function () {
      const { browser } = this;

      await browser.yaOpenStory('bank-card', 'default', {
        args: 'bank:atb;paymentSystem:jcb;cardNumber:•• 4100;money:300 USD',
      });

      await browser.assertView('default-money', elements.component);
    });

    it('withLabelMoney', async function () {
      const { browser } = this;

      await browser.yaOpenStory('bank-card', 'default', {
        args: 'bank:atb;paymentSystem:jcb;cardNumber:•• 4100;money:300 USD;label:label',
      });

      await browser.assertView('default-label-money', elements.component);
    });
  });

  describe('FamilyMember', function () {
    it('base', async function () {
      const { browser } = this;

      await browser.yaOpenStory('bank-card', 'family-member', {
        args: 'money:5000 ₽ на неделю',
      });

      await browser.pause(1500);

      await browser.assertView('family-member', elements.component);
    });

    it('isLoading', async function () {
      const { browser } = this;

      await browser.yaOpenStory('bank-card', 'family-member', {
        args: 'money:5000 ₽ на неделю',
      });

      await browser.assertView('family-member-loading', elements.component);
    });
  });

  describe('FamilyOwner', function () {
    it('base', async function () {
      const { browser } = this;

      await browser.yaOpenStory('bank-card', 'family-owner', {
        args: 'bank:atb;paymentSystem:jcb;cardNumber:•• 4100;',
      });

      await browser.assertView('family-owner', elements.component);
    });
  });

  describe('Preview', function () {
    it('base', async function () {
      const { browser } = this;

      await browser.yaOpenStory('bank-card', 'preview', {
        args: 'bank:akbars',
      });

      await browser.assertView('preview', elements.component);
    });

    it('familyMember', async function () {
      const { browser } = this;

      await browser.yaOpenStory('bank-card', 'preview-family-member');

      await browser.assertView('preview-family-member', elements.component);
    });
  });
});
