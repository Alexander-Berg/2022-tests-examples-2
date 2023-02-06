describe('Footer', function () {
  it('Default view', async function () {
    await this.browser.yaOpenStory('Footer', 'Default');
    await this.browser.assertView('plain', '#root');
  });

  it('English', async function () {
    await this.browser.yaOpenStory('Footer', 'Default', {
      globals: { locale: { id: 'en', name: 'En' } },
    });
    await this.browser.assertView('plain', '#root');
  });
});
