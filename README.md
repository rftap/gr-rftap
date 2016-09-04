# gr-rftap

## RFtap Module for GNU Radio

This module implements the [RFtap](https://rftap.github.io/) Encapsulation block, used to encapsulate Radio Frequency (RF) metadata about packets for Wireshark. Interoperability was tested with gr-rds, gr-ieee802-11, gr-ieee802-15-4.

You can connect the RFtap Encapsulation block in your flowgraphs to any block that has a PDU Message output port.

See: https://rftap.github.io/

## Installation

### GNU Radio

There are several ways to install GNU Radio. You can use

- [pybombs](http://gnuradio.org/redmine/projects/pybombs/wiki) (recommended)
- [pre-combiled binaries](http://gnuradio.org/redmine/projects/gnuradio/wiki/BinaryPackages)
- [from source](http://gnuradio.org/redmine/projects/gnuradio/wiki/InstallingGRFromSource)

### Simple Installation of gr-rftap using Package Manager

    pybombs install gr-rftap

### Manual Installation of gr-rftap

To manually install the blocks do

    git clone https://github.com/rftap/gr-rftap
    cd gr-rftap
    mkdir build
    cd build
    cmake ..
    make
    sudo make install
    sudo ldconfig

## Usage, Demos and Further information

See RDS and Wi-Fi flowgraphs in examples/ directory.

See: https://rftap.github.io/
