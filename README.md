# poetry-conda plugin

This plugin allows the installation of Poetry into Conda environments other than `base` and enables it to create
virtual environments for your projects without polluting the Conda environment where it is installed.

It works with any combination of Python 3.8+ and Poetry 1.3+.


## Installation

Inside a Conda environment, install the plugin using `pip`:

```bash
pip install poetry-conda
```


## Usage

This plugin adds the Poetry setting `virtualenvs.ignore-conda-envs` with a default value of `true`. When set to `true`,
Poetry will ignore Conda environments when creating virtual environments for your projects.

You can change this setting locally or globally the same way you would change any other Poetry setting, including through:

- the `poetry config` command
- Poetry environment variables
- the `poetry.toml` file
- the `pypoetry/config.toml` file


## Contributing

Contributions to this project are welcome. Please fork this repository, make your changes, and submit a pull request.


## License

This project is licensed under the terms of the MIT license.
