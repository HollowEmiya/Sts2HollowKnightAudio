extends SceneTree

func _initialize() -> void:
    var folder := "E:/EProjects/Sts2HollowKnightMod/Tools/FullVoidHeartAudioProject"
    if not OS.get_cmdline_user_args().is_empty():
        folder = OS.get_cmdline_user_args()[0]
    var rate := AudioServer.get_mix_rate()
    var frames := int(round(36.0 * rate))
    for stem in [2, 3]:
        var path: String = folder + "/Assets/music/music/S59-55 Final Stage %d.ogg" % stem
        var audio := AudioStreamOggVorbis.load_from_file(path)
        if audio == null or abs(audio.get_length() - 36.0) > 0.01:
            push_error("Unexpected source stem length: " + path)
            quit(1)
            return
        audio.loop = false
        var playback := audio.instantiate_playback()
        playback.start()
        var samples := playback.mix_audio(1.0, frames)
        var output := FileAccess.open(folder + "/Stem%d.f32" % stem, FileAccess.WRITE)
        output.store_buffer(samples.to_byte_array())
        output.close()
    var config := FileAccess.open(folder + "/DecodeInfo.json", FileAccess.WRITE)
    config.store_string(JSON.stringify({"rate":rate,"frames":frames}))
    config.close()
    print("PASS: decoded both complete 36-second HK stems at ", rate, "Hz.")
    quit()
