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
  pacific rocks, a farm dog answering the coyotes
- **[ keep .wav ]** downloads the last 90 seconds

the field research behind the casts — species by species, with
frequencies and timing for synthesis — is in the album's
`notes/usa.md`. the map is built from the public-domain US census
state outlines (`tools/make_map.py` regenerates `MAP_STATES` /
`MAP_COAST` from any us-states GeoJSON).

usa first; the globe is next.

no dependencies, no build, no server. open `index.html` or serve it
from anywhere static.
