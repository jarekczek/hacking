# hacking
hacking toolkit

## Python

### [Service controller](https://github.com/jarekczek/hacking/tree/main/python/service_controller)

To run different versions (configurations) of an arbitrary service (executable) and control it from
http protocol.

Configurations are organized in a set and numered from 1 to n.
After each invocation, the number is incremented, so that all configurations are used in sequence
(and looped).

#### Prerequisites

##### Service executable

Service means some program that may be started and stopped.
Once started it runs until getting stopped from the controller.

Service executable accepts a single integer argument, the number of a configuration to use.
The service must translate this integer into some configuration.

Configurations are numbered from 0 to CONFIG_COUNT-1.

The service is expected to act in the following manner (based on some concrete service,
for which this tool was designed):

- On success the service prints a message (SUCCESS_MESSAGE) and keeps running.
- On failure the service exits.

If the service keeps running, but does not display the success message, the controller keeps on waiting.
In other words - it hangs.
This is not desired and means that the controller is unable to control the service
and something needs to be changed.

When controller stops the service, it sends control-break to it.
The service should shut down after receiving this signal.

A sample windows service is provided as `example_service.bat`.

##### Environment variables

- CONFIG_COUNT number of configurations accepted by the service
- START_CONFIG (optional) number of first configuration to run (0 is the default)
- ESPEAK (optional) espeak executable for speech anouncements, silently ignored on error
- PORT http port on which to listen (only localhost)
- RETRIES (optional) max retries when starting the service, default is 3
- SERVICE path of the executable accepting single integer [0..CONFIG_COUNT)
- SUCCESS_MESSAGE a message printed by the service on success

#### Controller

Controller is a web application, that understands simple urls:

- /restart - stops the service if needed, starts until success (respecting RETRIES)
- /start - starts the service, then increments configuration number
- /stop - stops the service
- /shutdown - shuts down the controller

When service is being started, an integer number is passed as the argument.
This is the configuration number.
The configuration number is incremented on each invocation, to enable
starting the service each time with a different configuration.

#### Example service

`example_service.bat` is a simulation of a service. It has two configurations:

1. displays some messages, reports success, keeps running
2. displays some messages, stops running

So `1` is a successful start, `2` is showing a failure case.

After starting `service_controller.bat` one may issue server commands.
A reasonable sequence of command is like this:

1. start - would start a successful run
1. stop
1. start - would start a service which fails
1. one may loop from the beginning, as the previous start did not succeed
