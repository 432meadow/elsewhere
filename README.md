# elsewhere

an endless synthesized field recording of anywhere on earth.

**listen: https://432meadow.github.io/elsewhere/**

one html file. spin the globe — it turns on its own, drag it, pinch or
scroll to zoom, watch night cross the terminator — and tap anywhere:
you are standing there, now: the right
birds for that place singing at the right minute of its solar day,
crickets chirping at the rate its temperature says they should
(Dolbear's law), the wood thrush waiting for dusk, the whip-poor-will
stopping at sunrise. nothing is sampled — every voice is synthesized as
it plays, in the hyperrealism manner: pitch-contour whistles, resonant
pulse swarms, filtered noise, distance as lowpass + level + reverb.

- **the whole world**: outside the US the biome comes from the real
  Köppen–Geiger climate grid (Kottek et al. 2006, packed into 10 KB), so
  the deserts, monsoons and boreal belts are where they actually are.
  seasons flip at the equator — a sydney august dawn is a cold winter
  chorus of magpies and kookaburras; a tokyo july evening brings the
  higurashi; the serengeti night has the fiery-necked nightjar, hyenas,
  and — very far off, very rarely — lions. seven realms carry their own
  voices: nightingale and village bells in europe, gibbon duets and koels
  in asia, the screaming piha and howler monkeys on the amazon, the
  kookaburra riot and whipbird crack in australia
- **fourteen hand-drawn biomes** cover the lower 48 in extra detail —
  hardwood forest, boreal lakes, southern pine, the everglades, tallgrass
  and shortgrass prairie, three deserts, sagebrush, mountain conifer, the
  coastal rainforest, oak & chaparral, and both shores — each with its own
  cast (now ~130 species worldwide: birds, insects, frogs, mammals) and
  its own wind ([ usa ] on the map zooms in; [ world ] zooms back out)
- **the clock is real**: [ now ] follows the actual solar time at the
  site; the dawn chorus assembles in the true order (robins first);
  insects gate on modeled temperature; season comes from the date
- **[ a day in an hour ]** runs the sun 24× so you can listen to a whole
  day — the pre-dawn lull, the chorus, the midday cicadas, the dusk
  thrushes, the katydid wall — in one sitting
- **weather is seeded by site and day**: everyone listening to the same
  place on the same day gets the same wind, the same afternoon
  thunderstorm, the same fog morning; `?lat=&lon=&day=` replays a place
  ([ share this place ] copies the link)
- **the hyperreal details**: a high jet once or twice an hour, a far
  train horn on prairie nights, sea lions and a bell buoy off the
  pacific rocks, a farm dog answering the coyotes — and the land itself:
  leaf-rustle riding each gust, aspen flutter, tree creaks, seed-head
  rattle, autumn acorns dropping, frost cracks, lake ice singing its
  dispersion chirp across a frozen boreal lake
- **a fauna stem**: deer snorting and bounding off, squirrels scolding,
  chipmunks, prairie-dog towns, raccoons at night, bison on the
  shortgrass — alongside the coyotes, wolves and september elk — on
  their own fader
- **[ ∞ drift ]** sets the listener wandering anywhere on the landmass:
  a slow seeded walk whose bearing meanders and reflects off the coasts —
  creeks come and go, and every ten or twenty minutes you cross into
  another biome and the whole cast turns over (the journey is seeded by
  the day and the starting place, so a shared link wanders the same way)
- **[ dub ]** runs the land through a tape echo, after topdown dialectic:
  a rhythmic throw gate catches whatever the place is singing into a
  wobbling saturated feedback delay, over muted chord stabs and a soft
  sub pulse rooted in the site's own key (every place has one, from its
  coordinates). the treatment drifts on its own seeded weather — washing,
  sparse, deep, receding — and the field recording underneath stays
  untouched. a depth fader sets how deep it sits
- **[ keep .wav ]** downloads the last 90 seconds (recorded linear,
  before the live safety compressor — album convention)

the field research behind the casts — species by species, with
frequencies and timing for synthesis — is in the album's `notes/usa.md`
and `notes/global.md`. the maps are built from public-domain data: US
census state outlines (`tools/make_map.py`), natural earth 110m
countries + the köppen–geiger climate grid (`tools/make_world.py`).

no dependencies, no build, no server. open `index.html` or serve it
from anywhere static.
