Doc at `readthedocs <https://datasheet.readthedocs.io>`_

* Version 1.1.3
   * Automatically creates containing folder on instantiation
* Version 1.1.2
   * Has a new css template for pathfinder
* Version 1.1.1
   * Fixes a bug in gated cache, that wasn't caught by a test before (sorry)
* Version 1.1.0
    * Changes the default CSS to look way nicer, borrowed from 
        https://gist.github.com/killercup/5917178
    * adds stand alone mode
    * adds Layout classes.
    * Removes tuple interpretation by Sheet.__lshift__, use the Layouts instead
* Version 1.0.1
    * set matplotlibs rendering back-end to agg before importing pyplot, so that 
        the library does not depend on tkinter
* Version 1.0 - release
