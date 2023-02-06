import {Zippable, zipSync} from 'fflate';
import fs from 'fs';
import os from 'os';
import path from 'path';

type ArchiveExt = 'zip';
type ArchiveName = `${string}.${ArchiveExt}`;

/**
 * @description Создает архив файлов, записывает на диск во временную директорию ОС, возвращает путь
 * @param name Имя файла
 * @param filePaths Пути до файлов, которые необходимо добавить в архив
 */
export default async function createArchive(name: ArchiveName, filePaths: string[]) {
    const zippable: Zippable = {};
    for (const filePath of filePaths) {
        const name = path.basename(filePath);
        const buff = fs.readFileSync(filePath);
        zippable[name] = buff;
    }
    const archiveBuff = zipSync(zippable, {level: 9});

    const dirName = os.tmpdir();
    const pathToFile = path.join(dirName, name);
    await fs.promises.writeFile(pathToFile, archiveBuff);

    return pathToFile;
}
