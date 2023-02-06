import kleur from 'kleur';

export function writeInfo(msg: string) {
    return console.log(kleur.cyan().bold(msg));
}
