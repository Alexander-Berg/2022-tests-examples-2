export interface Fillable {
    fill(value: string): Promise<void>;
}
