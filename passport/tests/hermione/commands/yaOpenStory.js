module.exports = function (id, storyName, params) {
  if (!id) {
    throw new TypeError('Invalid parameter: id');
  }

  if (!storyName) {
    throw new TypeError('Invalid parameter: storyName');
  }

  const searchParams = new URLSearchParams({
    id: `${id}--${storyName}`,
    viewMode: 'story',
    ...params,
  });

  return this.url('/storybook/iframe.html?' + searchParams);
};
