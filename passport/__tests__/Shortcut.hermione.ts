describe('Shortcut', () => {
  const elements = {
    container: "[data-testid='container']",
    shortcut: "[data-testid='shortcut']",
  };

  it(`common`, async function () {
    const { browser } = this;

    await browser.yaOpenStory('hermione-shortcut', 'common');

    await browser.assertView('plain', elements.container);
  });

  ['default', 'pay', 'plus', 'family'].forEach((variant) => {
    it(`interactive ${variant}`, async function () {
      const { browser } = this;

      await browser.yaOpenStory('hermione-shortcut', 'interactive', { args: `variant:${variant}` });
      const shortcut = await browser.$(elements.shortcut);

      await browser.assertView('plain', elements.container);

      await shortcut.moveTo();
      await browser.assertView('hovered', elements.container);
    });
  });

  it('interactive disabled', async function () {
    const { browser } = this;

    await browser.yaOpenStory('hermione-shortcut', 'interactive', { args: 'disabled:true' });
    const shortcut = await browser.$(elements.shortcut);

    await browser.assertView('plain', elements.container);

    await shortcut.moveTo();
    await browser.assertView('hovered', elements.container);
  });
});
