================
stl: time logger
================

A cli time logger. Diligently make logs when you switch on/off the working mode
and it will dutifully do the arithmetics.


usage
=====

The time from the moment you do::

    stl start lumberjacking

until the moment you do::

    stl stop

will be added to the time logs. Once your logs start piling up, you can fulfil
your working hours curiousity::

    stl show --task lumberjacking
    stl show --month october
    stl show --span 15 oct 5 dec

Check ``stl show --help`` for all the options, there are a few of these. The
data is stored in plaintext files in ``~/.config/stl``, safe to move around or
version control.


installation
============

This is a standard Python 3 package installable through pip and without
dependencies::

    pip install stltimelogger


docs
====

* ``stl start`` makes a log that you start working. You can also add a task
  name if you want to see stats about that particular task later on.

* ``stl stop`` makes a log that you have stopped working.

* ``stl show`` (also ``stl status``) shows you how far you are into your
  current task when called without additional arguments. The latter might be:

    * ``stl show --day DAY`` (also ``-d``) where ``DAY`` can be anything like:
      ``15 oct 2016``, ``october 15``, ``15``, ``2016-10-15``, ``today``,
      ``yesterday``, ``this``, ``last``.
    * ``stl show --week WEEK`` (also ``-w``) where ``WEEK`` can be either
      ``this`` or ``last``.
    * ``stl show --month MONTH`` (also ``-m``) where ``MONTH`` can be anything
      like: ``oct``, ``oct 2016``, ``2016 oct``, ``october``, ``10``, ``this``,
      ``last``.
    * ``stl show --year YEAR`` (also ``-y``) where ``YEAR`` can be anything
      like: ``2016``, ``16``, ``this``, ``last``.
    * ``stl show --span SPAN`` (also ``-s``) where ``SPAN`` can be anything
      like: ``15 25 oct``, ``15 oct 2016 25 oct 2016``, ``15 25``, ``15``. If
      you specify only one date, the second will be set to today; e.g. ``stl
      show -s 1 oct`` is the same as ``stl show -m oct``. The interval is
      inclusive at both ends.
    * ``stl show --task TASK`` (also ``-t``) where ``TASK`` is the name of a
      task you have prudently specified when you had been working on it.

* ``stl add START STOP [TASK]`` allows you to cheat and add log entries for
  arbitrary time intervals in the past and future.

* ``stl edit WHAT`` opens the right file in your $EDITOR. ``WHAT`` can be anything
  which is a valid ``stl show -m`` argument. As you might guess, logs are
  stored in month files.


similar projects
================

* `timeflow <https://github.com/trimailov/timeflow>`_: also in Python but
  somewhat different approach.
* `taskwarrior <https://taskwarrior.org/>`_: a great todo cli manager which
  includes time logging functionality as well.


licence
=======

MIT. Do as you please and praise the snake gods.
