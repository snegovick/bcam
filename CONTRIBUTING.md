# Fork and clone

Start by creating a fork of the [GitHub repository]
(https://github.com/snegovick/bcam) and clone it to your computer.
See [GitHub's instructions](https://help.github.com/articles/fork-a-repo/).


# Install dependencies

Developing BCAM requires [Python 2.7](https://www.python.org/), [PyGTK]
(http://www.pygtk.org/), and [Tox](http://tox.testrun.org/) to be
pre-installed.  If you are on a recent version of Debian or Ubuntu, you can
install these by running:

    sudo apt-get install python-gtk2 python-tox


# Generate environment

Go into the cloned repository and run:

    tox -e devenv

This will generate an environment containing all development libraries in
`.tox/devenv`.  Activate the environment by running:

    source .tox/devenv/bin/activate

Or, if you're on Windows:

    .tox\devenv\Scripts\activate


# Running

Now, your in-development copy of BCAM can be run just by executing:

    bcam-launcher

Before committing, make sure to run the automated tests by running:

    tox
