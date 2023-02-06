describe('ProgressCircle', function () {
  const elements = {
    element: "[data-testid='element']",
  };

  describe('sizes', () => {
    [16, 24, 32, 36, 44].forEach((size) => {
      it(`size-${size}`, async function () {
        const { browser } = this;

        await browser.yaOpenStory('progress-circle', 'default', {
          args: `size:${size}`,
        });

        await browser.assertView('plain', elements.element);
      });
    });
  });

  describe('variants', () => {
    ['default', 'brand'].forEach((variant) => {
      it(`variant-${variant}`, async function () {
        const { browser } = this;

        await browser.yaOpenStory('progress-circle', 'default', {
          args: `variant:${variant};value:45`,
        });

        await browser.assertView('plain', elements.element);
      });
    });
  });

  describe('format style', () => {
    ['decimal', 'percent'].forEach((formatStyle) => {
      it(`format-style-${formatStyle}`, async function () {
        const { browser } = this;

        await browser.yaOpenStory('progress-circle', 'default', {
          args: `formatStyle:${formatStyle};value:3;min:0;max:4;size:44;strokeWidth:3`,
        });

        await browser.assertView('plain', elements.element);
      });
    });
  });

  it('counterclockwise', async function () {
    const { browser } = this;

    await browser.yaOpenStory('progress-circle', 'default', {
      args: `clockwise:false;value:35`,
    });

    await browser.assertView('plain', elements.element);
  });

  it('gradient', async function () {
    const { browser } = this;

    await browser.yaOpenStory('progress-circle', 'gradient');

    await browser.assertView('plain', elements.element);
  });

  it('dynamic color', async function () {
    const { browser } = this;

    await browser.yaOpenStory('progress-circle', 'dynamic-color', { args: 'value:15' });
    await browser.assertView('progress-0', elements.element);

    await browser.yaOpenStory('progress-circle', 'dynamic-color', { args: 'value:35' });
    await browser.assertView('progress-25', elements.element);

    await browser.yaOpenStory('progress-circle', 'dynamic-color', { args: 'value:65' });
    await browser.assertView('progress-50', elements.element);

    await browser.yaOpenStory('progress-circle', 'dynamic-color', { args: 'value:85' });
    await browser.assertView('progress-100', elements.element);
  });

  it('progress', async function () {
    const { browser } = this;

    await browser.yaOpenStory('progress-circle', 'default', {
      args: 'value:0;max:100;size:36;formatStyle:percent',
    });
    await browser.assertView('start', elements.element);

    await browser.yaOpenStory('progress-circle', 'default', {
      args: 'value:100;max:100;size:36;formatStyle:percent',
    });
    await browser.assertView('end', elements.element);
  });
});
