package android.os;

import androidx.annotation.Nullable;

public class Looper {
    public static @Nullable
    Looper myLooper() {
        return null;
    }

    public static @Nullable
    Looper getMainLooper() {
        return new Looper();
    }
}
