# stl: time logger

Yet another cli time logger. Diligently make logs when you switch on/off the
working mode and it will dutifully do the arithmetics.


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

Check `stl show --help` for all the options, there are a few of these. The data
is stored in plaintext files in `~/.config/stl`, safe to move around or version
control them.


## installation

This is a standard Python 3 package installable through pip and without
dependencies.


## docs

* `stl start` makes a log that you start working. You can also add a task name
  if you want to see stats about that particular task later on.
* `stl stop` makes a log that you have stopped working.
* `stl show` (also `stl status`) shows you how far you are into your current
  task when called without additional arguments. The latter might be:
	* `stl show --day DAY` (also `-d`) where DAY can be anything like: 15 oct
	  2016, october 15, 15, 2016-10-15, today, yesterday, this, last.
	* `stl show --week WEEK` (also `-w`) where WEEK can be either this or last.
	* `stl show --month MONTH` (also `-m`) where MONTH can be anything like:
	  oct, oct 2016, 2016 oct, october, 10, this, last.
	* `stl show --year YEAR` (also `-y`) where YEAR can be anything like: 2016,
	  16, this, last.
	* `stl show --task TASK` (also `-t`) where TASK is the name of a task you
	  have prudently specified when you had been working on it.
* `stl add START STOP [TASK]` allows you to cheat and add log entries for
  arbitrary time intervals in the past and future.
* `stl edit WHAT` opens the right file in your $EDITOR. WHAT can be anything
  which is a valid `stl show -m` argument. As you might guess, logs are stored
  in month files.


## similar projects

* [timeflow](https://github.com/trimailov/timeflow): also python but somewhat
  different approach.


## licence

MIT. Do as you please and praise the snake gods.
