# stl: time logger

Yet another cli time logger.


## usage

The time from the moment you do:

```bash
stl start lumberjacking
```

until the moment you do:

```bash
stl stop
```

will be added to the time logs. Once your logs start piling up, you can fulfil
your working hours curiousity:

```bash
stl show --task lumberjacking
stl show --month october
```

Apart from the expected artihmetics, you will be presented with beautiful
console diagrams.


## installation

This is a standard Python 3 package installable through pip and without
dependencies. The data is stored in human-readable files in either
`~/.config/stl` or `~/.stl` (if there is not a `~/.config` dir already).


## licence

MIT. Do as you please and praise the snake gods.
