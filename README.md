# Python Essentials 

Collection of python utility modules

By Kami-Kaze

# Installing
Run `pip install git@<git repo>`

if building the spdlog wheel fails, just run the command again, by that time pybind11 will be present.

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