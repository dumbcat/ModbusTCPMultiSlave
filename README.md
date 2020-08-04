# Query multiple IO status in multiple Modbus TCP client

+ **Main Features**

  + Polling the IO status of multiple modbus tcp clients according to the settings of the ini file

  + Logging the time and content of the exceptions


## Require Packages

+ configparser

+ pymodbus

## Structure

+ **modbus&#46;py:** Read the ini file and polling the modbus tcp slaves, and finally display the result.

+ **modbus.ini:** Parameters needed to run the program.

# INI file

+ **Remote host:**

<pre><code>[<i>&lt;custom slave name></i>]
ip = <i>&lt;slave ip address></i>
port = <i>&lt;1slave modbus tcp port></i>
unit = <i>&lt;the slave unit this request is targeting></i>

ai_enable = <i>&lt;1: enable polling AI status, 0: disable></i>
ai_address = <i>&lt;the starting address to read></i>
ai_count = <i>&lt;the number of registers to read></i>

ao_enable = <i>&lt;1: enable polling AO status, 0: disable></i>
ao_address = <i>&lt;the starting address to read></i>
ao_count = <i>&lt;the number of registers to read></i>

di_enable = <i>&lt;1: enable polling DI status, 0: disable></i>
di_address= <i>&lt;the number of discretes to read></i>
di_count = <i>&lt;the number of registers to read></i>

do_enable = <i>&lt;1: enable polling DO status, 0: disable></i>
do_address= <i>&lt;the starting address to read></i>
do_count = <i>&lt; the number of coils to read></i>
</code></pre>

## Attention

The program is design for polls all IO every second. Each time an exception generated, there will be a one-second timeout, and the polling time will be **increased by one second**.

# Reference

&#91;1] https://pymodbus.readthedocs.io/en/latest/source/example/synchronous_client.html