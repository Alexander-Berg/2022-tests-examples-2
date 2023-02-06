'use strict';

Java.perform(function() {
    var i = 0; 

    var audioRecord = Java.use("android.media.AudioRecord");
    audioRecord.read.overload('java.nio.ByteBuffer', 'int', 'int').implementation = function(audioBuffer, sizeInBytes, readMode) {
        i++;
        console.log(i + ": read 1")
        return this.read(audioBuffer, sizeInBytes, readMode);
    }
    audioRecord.read.overload('java.nio.ByteBuffer', 'int').implementation = function(audioBuffer, sizeInBytes) {
        i++;
        console.log(i + ": read 2")
        return this.read(audioBuffer, sizeInBytes);
    }
    audioRecord.read.overload('[B', 'int', 'int').implementation = function(audioBytes, offset, sizeInBytes) {
        i++;
        console.log(i + ": read 3")
        return this.read(audioBytes, offset, sizeInBytes);
    }
    audioRecord.read.overload('[S', 'int', 'int').implementation = function(audioBytes, offset, sizeInBytes) {
        i++;
        console.log(i + ": read 4")
        return this.read(audioBytes, offset, sizeInBytes);
    }
    audioRecord.read.overload('[B', 'int', 'int', 'int').implementation = function(audioBytes, offset, sizeInBytes, readMode) {
        i++;
        console.log(i + ": read 5")
        return this.read(audioBytes, offset, sizeInBytes, readMode);
    }
    audioRecord.read.overload('[F', 'int', 'int', 'int').implementation = function(audioBytes, offset, sizeInBytes, readMode) {
        i++;
        console.log(i + ": read 6")
        return this.read(audioBytes, offset, sizeInBytes, readMode);
    }
    audioRecord.read.overload('[S', 'int', 'int', 'int').implementation = function(audioBytes, offset, sizeInBytes, readMode) {
        i++;
        console.log(i + ": read 7")
        return this.read(audioBytes, offset, sizeInBytes, readMode);
    }

});
