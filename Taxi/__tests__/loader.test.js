const { webpack } = require('./helpers');

describe('loader', () => {
  it('should compile with `js` entry point', async () => {
    const stats = await webpack('basic.js', {}, {}); // output: true
    const { modules } = stats.toJson();
    const loader = modules.find(
      module => module.id === './src/__tests__/fixtures/basic.css'
    );

    expect(loader.source).toMatchSnapshot('source');
    expect(stats.compilation.warnings).toMatchSnapshot('warnings');
    expect(stats.compilation.errors).toMatchSnapshot('errors');
  });

  it('should compile with `js` entry point and CSS extracted', async () => {
    const stats = await webpack('basic.js', {}, { extractCSS: true });
    const { modules } = stats.toJson();
    const loader = modules.find(
      module => module.id === './src/__tests__/fixtures/basic.css'
    );

    expect(loader.source).toMatchSnapshot('source');
    expect(stats.compilation.warnings).toMatchSnapshot('warnings');
    expect(stats.compilation.errors).toMatchSnapshot('errors');
  });

  it('should compile with `js` entry point with stylus', async () => {
    const stats = await webpack('stylus.js', {}, {}); // output: true
    const { modules } = stats.toJson();
    const loader = modules.find(
      module => module.id === './src/__tests__/fixtures/stylus.styl'
    );

    expect(loader.source).toMatchSnapshot('source');
    expect(stats.compilation.warnings).toMatchSnapshot('warnings');
    expect(stats.compilation.errors).toMatchSnapshot('errors');
  });

  it('should compile with `js` entry point with stylus and CSS extracted', async () => {
    const stats = await webpack('stylus.js', {}, { extractCSS: true });
    const { modules } = stats.toJson();
    const loader = modules.find(
      module => module.id === './src/__tests__/fixtures/stylus.styl'
    );

    expect(loader.source).toMatchSnapshot('source');
    expect(stats.compilation.warnings).toMatchSnapshot('warnings');
    expect(stats.compilation.errors).toMatchSnapshot('errors');
  });
});
