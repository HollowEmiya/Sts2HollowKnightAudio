var events=studio.project.model.Event.findInstances();
if(events.length!==71)throw new Error('Expected 71 events, got '+events.length);
var loopCount=0,musicCount=0;
events.forEach(function(e){
    if(e.groupTracks.length!==1)throw new Error('Missing track '+e.name);
    var sounds=e.timeline.modules;
    if(sounds.length!==1 || !sounds[0].audioFile || !(sounds[0].audioFile.length>0))throw new Error('Missing audio '+e.name);
    if(!e.groupTracks[0].modules[0] || e.groupTracks[0].modules[0].id!==sounds[0].id)throw new Error('Track assignment '+e.name);
    var music=(e.banks[0].name==='HK_Emiya_Music'||e.banks[0].name==='HK_Emiya_VoidHeart');
    if(music)musicCount++;
    var bus=studio.project.lookup(music?'bus:/master/music':'bus:/master/sfx');
    if(e.mixerInput.output.id!==bus.id)throw new Error('Wrong bus '+e.name);
    if(music&&!sounds[0].audioFile.isStreaming)throw new Error('Music not streaming '+e.name);
    e.timeline.markers.forEach(function(r){if(r.isOfExactType('LoopRegion')){
        loopCount++;var full=e.name==='void_heart_birthplace';var expectedLength=full?36:sounds[0].audioFile.length;var expectedStart=full?72:0;if(!r.looping||!r.markerTrack||Math.abs(r.length-expectedLength)>0.001||Math.abs(r.position-expectedStart)>0.001)throw new Error('Invalid loop '+e.name);if(full&&Math.abs(sounds[0].audioFile.length-108)>0.001)throw new Error('Void Heart is not the complete arrangement');
    }});
});
if(musicCount!==17||loopCount!==20)throw new Error('Unexpected music/loops '+musicCount+'/'+loopCount);
console.log('PASS: 71 events, 54 SFX, 17 streaming music, 20 loops; assets, tracks, banks and routing verified.');

