describe('Button', () => {
  const elements = {
    container: "[data-testid='container']",
    button: "[data-testid='button']",
  };

  ['m', 'l', 'xl'].forEach((size) => {
    it(`common size ${size}`, async function () {
      const { browser } = this;

      await browser.yaOpenStory('hermione-button', 'common', {
        args: `size:${size}`,
      });

      await browser.assertView('plain', elements.container);
    });
  });

  it('commom disabled', async function () {
    const { browser } = this;

    await browser.yaOpenStory('hermione-button', 'common', {
      args: `disabled:true`,
    });

    await browser.assertView('plain', elements.container);
  });

  it('text', async function () {
    const { browser } = this;

    await browser.yaOpenStory('hermione-button', 'text');

    await browser.assertView('plain', elements.container);
  });

  it('icons', async function () {
    const { browser } = this;

    await browser.yaOpenStory('hermione-button', 'icons');

    await browser.assertView('plain', elements.container);
  });

  hermione.skip.in(/./, 'Не работает buttonDown и key uE004');
  it('interactive', async function () {
    const { browser } = this;

    await browser.yaOpenStory('hermione-button', 'interactive');
    const button = await browser.$(elements.button);

    await browser.assertView('plain', elements.container);

    await button.moveTo();
    await browser.assertView('hovered', elements.container);

    await button.buttonDown();
    await browser.assertView('pressed', elements.container);

    await browser.keys('\uE004');
    await browser.assertView('focused', elements.container);
  });
});
