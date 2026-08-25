# elsewhere

an endless synthesized field recording of anywhere in america.

**listen: https://432meadow.github.io/elsewhere/**

one html file. click the map and you are standing there, now: the right
birds for that biome singing at the right minute of that place's solar
day, crickets chirping at the rate its temperature says they should
(Dolbear's law), the wood thrush waiting for dusk, the whip-poor-will
stopping at sunrise. nothing is sampled — every voice is synthesized as
it plays, in the hyperrealism manner: pitch-contour whistles, resonant
pulse swarms, filtered noise, distance as lowpass + level + reverb.

- **fourteen biomes** cover the lower 48 — hardwood forest, boreal lakes,
  southern pine, the everglades, tallgrass and shortgrass prairie, three
  deserts, sagebrush, mountain conifer, the coastal rainforest, oak &
  chaparral, and both shores — each with its own cast (~85 species:
  birds, insects, frogs, mammals) and its own wind
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
- **[ ∞ drift ]** sets the listener wandering: a slow seeded walk whose
  bearing meanders and reflects off the coasts — creeks come and go,
  and every ten or twenty minutes you cross into another biome and the
  whole cast turns over (the journey is seeded by the day and the
  starting place, so a shared link wanders the same way)
- **[ keep .wav ]** downloads the last 90 seconds; **[ keep stems ]**
  downloads the same 90 seconds as birds / insects / frogs / fauna /
  air / space WAVs that sum back to the mix exactly (the recorded mix
  is linear, album convention — the live compressor is not printed)

the field research behind the casts — species by species, with
frequencies and timing for synthesis — is in the album's
`notes/usa.md`. the map is built from the public-domain US census
state outlines (`tools/make_map.py` regenerates `MAP_STATES` /
`MAP_COAST` from any us-states GeoJSON).

usa first; the globe is next.

no dependencies, no build, no server. open `index.html` or serve it
from anywhere static.
