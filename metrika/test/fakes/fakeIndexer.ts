export default class FakeIndexer {
  index = new Map<number, HTMLElement>()
  document: Document

  constructor (document: Document) {
    this.document = document
  }

  add (id: number, element: HTMLElement) {
    this.index.set(id, element)
  }

  findByID (id: number) {
    return this.find(id)
  }

  find (id: number) {
    return this.index.get(id)
  }
}