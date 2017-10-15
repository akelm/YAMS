PDF version of this README is in [docs/README.pdf](docs/README.pdf)

#YAMS -- yet another Mie smulator
A Python programme with GUI to calculate

#Installation
##Running with Python interpreter (recommended)
###Prerequisites
* Python 3.5.3 (although any Python 3.x should do)
On Linux Python 3.x should be available in your distribution repositories. Debian/Ubuntu:
```bash
sudo apt-get install python3
```
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For Windows, check here: https://www.python.org/downloads/

* NumPy >= 1.13.3
* SciPy >= 0.18.1
* scikit-learn >= 0.19.0
* yaml >= 3.12
* matplotlib >= 2.1.0 (assuming you need plotting)
* psutil >= 5.0.1

Since Python 3.4, ```pip``` is included by default, so in order to install the above Python packages you need:
```bash
python3 -m pip numpy scipy sklearn yaml matplotlib psutil
```
For Python &lt; 3.4, I guess you first need to get ```pip``` from https://pip.pypa.io/en/stable/installing/.
###Running
Enter the folder ```yams``` and run:
```bash
cd yams
python3 ./yams.py
```
###Utilizing package components
The following may turn useful for those who might need some scripting. 'The heart' of the package is ```yams/fluoroph1layer2.py``` to wchich you can pass input files, savename and chosen fluorophores directly. Check more in the comments of  ```yams/fluoroph1layer2.py```.
##Running from binaries (Linux amd64)
Download [tar.gz archive](dist/yams-amd64.tar.gz)(~70 MB), and extract it:
```bash
tar -zxvf yams-amd64.tar.gz
```
Run it either double-clicking on the ```dist/yams``` file or from the commandline:
```bash
cd dist/yams
./yams
```
Tested on fresh install of Ubuntu 16.04.3 Desktop (Xenial Xerus).
**Pros**: No need to install Python and extra packages.
**Cons**: Archive is around 70MB as YAMS was written in pure Python and binaries were made with PyIstaller.
#Usage
##User interface
##Input files
All input files, as well as settings file are give in ```yaml``` format. Current specifications of the format are given in http://yaml.org/spec/1.2/spec.html. In fact, on the basis of existing files one can create their own without checking ```yaml``` specifications.
###Geometry
Sample geometry files are contained in ```input_files``` folder and it is advised to save the newly created files also there. The files contain all the information needed to compute transfer matrices and enhancement factors. Sample geometry file with comments is in ```input_files/c510test_sample.yaml```. In doubt, you can always save input file generated in GUI by choosing ```file > save input as``` or load the file by ```file >load input file```.
###Photophysics

##Output files

##Advanced
###Settings
Advanced settings are in ```pkg_resources/setting.yaml```. These inculde multiprocessing, vector spherical harmonics (VSH) series truncation in case on non-convergence and plotting options. Check comments of ```pkg_resources/setting.yaml```.
###
#Credits
Contact: annamariakelm@gmail.com, GitHub: https://github.com/akelm

#How to cite

#Acknowledgements

#License
Copyright (C) 2017 Anna Kelm

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

[License file](LICENCSE)