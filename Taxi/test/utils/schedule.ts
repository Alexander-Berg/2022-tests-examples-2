const MS_IN_MIN = 60000;

function padTo2Digits(num: number) {
    return num.toString().padStart(2, '0');
}

function convertMsToHM(milliseconds: number) {
    let seconds = Math.floor(milliseconds / 1000);
    let minutes = Math.floor(seconds / 60);
    let hours = Math.floor(minutes / 60);

    seconds = seconds % 60;
    // If seconds are greater than 30, round minutes up (optional)
    minutes = seconds >= 30 ? minutes + 1 : minutes;

    minutes = minutes % 60;

    // If you don't want to roll hours over, e.g. 24 to 00
    // comment (or remove) the line below
    // commenting next line gets you `24:00:00` instead of `00:00:00`
    // or `36:15:31` instead of `12:15:31`, etc.
    hours = hours % 24;

    return `${padTo2Digits(hours)}:${padTo2Digits(minutes)}`;
}

function formatTimeDependsOnMins(hhmm: string) {
    const hh_mm = hhmm.split(':');
    const mm = hh_mm[1];

    if (mm === '00') {
        return hh_mm[0];
    } else {
        return hhmm;
    }
}

export function makeNameForSimpleSchedule(work: number, weekend: number, start: string, duration: number) {
    const parsedStart =  new Date('1970-01-01T' + start + ':00Z');
    const durationMs = duration * MS_IN_MIN; // длительность в мс
    const finishMs = parsedStart.getTime() + durationMs;
    const finish = convertMsToHM(finishMs);

    const startStr = formatTimeDependsOnMins(start);
    const finishStr = formatTimeDependsOnMins(finish);

    return work + '/' + weekend + ' | ' + startStr + '-' + finishStr;
}
