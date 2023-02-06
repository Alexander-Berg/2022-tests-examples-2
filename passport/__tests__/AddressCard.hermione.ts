hermione.skip.in(/./);
describe('AddressCard', function () {
  const elements = {
    component: "[data-testid='element']",
  };

  describe('Default', function () {
    it('base', async function () {
      const { browser } = this;

      await browser.yaOpenStory('address-card', 'default');

      await browser.assertView('default', elements.component);
    });
  });

  describe('New', function () {
    it('base', async function () {
      const { browser } = this;

      await browser.yaOpenStory('address-card', 'new', {
        args: 'addressType:Дом',
      });

      await browser.assertView('new', elements.component);
    });
  });
});
