'use strict';

Java.perform(function() {
    var i = 0; 

    var audioTrack = Java.use("android.media.AudioTrack");
    audioTrack.write.overload('java.nio.ByteBuffer', 'int', 'int').implementation = function(audioBuffer, sizeInBytes, writeMode) {
        i++;
        console.log(i + ": write 1")
        return this.write(audioBuffer, sizeInBytes, writeMode);
    }
    audioTrack.write.overload('java.nio.ByteBuffer', 'int', 'int', 'long').implementation = function(audioBuffer, sizeInBytes, timestamp) {
        i++;
        console.log(i + ": write 2")
        return this.write(audioBuffer, sizeInBytes, timestamp);
    }
    audioTrack.write.overload('[B', 'int', 'int').implementation = function(audioBytes, offset, sizeInBytes) {
        i++;
        console.log(i + ": write 3")
        return this.write(audioBytes, offset, sizeInBytes);
    }
    audioTrack.write.overload('[S', 'int', 'int').implementation = function(audioBytes, offset, sizeInBytes) {
        i++;
        console.log(i + ": write 4")
        return this.write(audioBytes, offset, sizeInBytes);
    }
    audioTrack.write.overload('[B', 'int', 'int', 'int').implementation = function(audioBytes, offset, sizeInBytes, writeMode) {
        i++;
        console.log(i + ": write 5")
        return this.write(audioBytes, offset, sizeInBytes, writeMode);
    }
    audioTrack.write.overload('[F', 'int', 'int', 'int').implementation = function(audioBytes, offset, sizeInBytes, writeMode) {
        i++;
        console.log(i + ": write 6")
        return this.write(audioBytes, offset, sizeInBytes, writeMode);
    }
    audioTrack.write.overload('[S', 'int', 'int', 'int').implementation = function(audioBytes, offset, sizeInBytes, writeMode) {
        i++;
        console.log(i + ": write 7")
        return this.write(audioBytes, offset, sizeInBytes, writeMode);
    }
});
