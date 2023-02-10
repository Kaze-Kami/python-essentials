# Python Essentials 

Collection of python utility modules

By Kami-Kaze

# Installing
To build spdlog `pybind11` is required.
Either install it manually, or run the pip 
command twice (the first one will fail to install spdlog but install `pybind11`)

- Pip: `pip install git+https://github.com/Kaze-Kami/python-essentials.git`
- Requirements.txt: `python-essentials @ git+https://github.com/Kaze-Kami/python-essentials.git`
 
**NB:** If you need to update due to repo changes run pip with `--upgrade --force-reinstall`

# IO
**IO Module**
## Format
- Text Formatting

## Logging
> Simple wrapper around python-spdlog
- use `get_logger('logger name')`

> Global log level can configured via environment

Available log levels are (config is case insensitive):
- `critical`
- `error`
- `warning`
- `info`
- `debug`
- `trace`
- `none`

Configure environment variable using `log_level=<log level>`

# Containers
**Data containers**

- `PathDict`: A dictionary that supports (sub-) entry access with 'paths.with.dots'


# GUI
**GUI using pyimgui and opengl**