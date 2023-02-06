export class Mock {
    request: RegExp;
    response: any;
    constructor(request: RegExp, response: any) {
        this.request = request;
        this.response = response;
    }
}
