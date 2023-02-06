import {HtmlMarkup, getContentBetweenTags} from './html-markup'

describe('HtmlMarkup provider', () => {
  const templateScope = 'test'
  const templateSections: ('foo' | 'bar' | 'baz')[] = ['foo', 'bar', 'baz', 'foo']

  const DETECTOR_BEGIN = '<!-- test_detector__begin -->'
  const DETECTOR_END = '<!-- test_detector__end -->'
  const fooSection = (content?: string) =>
    `<!-- test_section_foo_begin -->${content ?? ''}<!-- test_section_foo_end -->`
  const barSection = (content?: string) =>
    `<!-- test_section_bar_begin -->${content ?? ''}<!-- test_section_bar_end -->`
  const bazSection = (content?: string) =>
    `<!-- test_section_baz_begin -->${content ?? ''}<!-- test_section_baz_end -->`

  it('should handle "getContentBetweenTags()" method', () => {
    const markup = new HtmlMarkup({content: '', templateScope, templateSections})
    const {begin: beginTag, end: endTag} = markup.getMarkupTag('section', 'sample')

    let result = getContentBetweenTags('', beginTag, endTag)
    expect(result).toBeUndefined()

    result = getContentBetweenTags(beginTag + endTag, beginTag, endTag)
    expect(result).toStrictEqual({before: '', between: '', after: ''})

    result = getContentBetweenTags(`foo${beginTag}${endTag}`, beginTag, endTag)
    expect(result).toStrictEqual({before: 'foo', between: '', after: ''})

    result = getContentBetweenTags(`${beginTag}${endTag}foo`, beginTag, endTag)
    expect(result).toStrictEqual({before: '', between: '', after: 'foo'})

    result = getContentBetweenTags(`${beginTag}foo${endTag}`, beginTag, endTag)
    expect(result).toStrictEqual({before: '', between: 'foo', after: ''})

    result = getContentBetweenTags(`foo${beginTag}bar${endTag}baz`, beginTag, endTag)
    expect(result).toStrictEqual({before: 'foo', between: 'bar', after: 'baz'})
  })

  it('should extend sections', () => {
    const markup = new HtmlMarkup({content: 'test', templateScope, templateSections})

    let content = markup.extend({foo: 'foo'})
    expect(content).toBe(
      'test' + DETECTOR_BEGIN + fooSection('foo') + barSection() + bazSection() + fooSection('foo') + DETECTOR_END,
    )

    content = markup.extend({bar: 'bar', baz: 'baz'})
    expect(content).toBe(
      'test' +
        DETECTOR_BEGIN +
        fooSection('foo') +
        barSection('bar') +
        bazSection('baz') +
        fooSection('foo') +
        DETECTOR_END,
    )

    content = markup.extend({foo: '', bar: '', baz: ''})
    expect(content).toBe(
      'test' + DETECTOR_BEGIN + fooSection() + barSection() + bazSection() + fooSection() + DETECTOR_END,
    )
  })

  it('should insert content before template', () => {
    const contentBefore = 'before'
    const markup = new HtmlMarkup({content: 'test', templateScope, templateSections, contentBefore})
    const content = markup.extend({bar: 'bar'})
    expect(content).toBe(
      'test' +
        contentBefore +
        DETECTOR_BEGIN +
        fooSection() +
        barSection('bar') +
        bazSection() +
        fooSection() +
        DETECTOR_END,
    )
  })

  it('should insert content after template', () => {
    const contentAfter = 'after'
    const markup = new HtmlMarkup({content: 'test', templateScope, templateSections, contentAfter})
    const content = markup.extend({bar: 'bar'})
    expect(content).toBe(
      'test' +
        DETECTOR_BEGIN +
        fooSection() +
        barSection('bar') +
        bazSection() +
        fooSection() +
        DETECTOR_END +
        contentAfter,
    )
  })

  it('should handle content with line breaks', () => {
    const markup = new HtmlMarkup({content: 'test', templateScope, templateSections})

    let content = markup.extend({foo: '\nfoo\n'})
    expect(content).toBe(
      'test' +
        DETECTOR_BEGIN +
        fooSection('\nfoo\n') +
        barSection() +
        bazSection() +
        fooSection('\nfoo\n') +
        DETECTOR_END,
    )

    content = markup.extend({bar: '\nbar\n'})
    expect(content).toBe(
      'test' +
        DETECTOR_BEGIN +
        fooSection('\nfoo\n') +
        barSection('\nbar\n') +
        bazSection() +
        fooSection('\nfoo\n') +
        DETECTOR_END,
    )
  })
})
