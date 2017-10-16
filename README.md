PDF version of this README is in [docs/README.pdf](docs/README.pdf)

# YAMS -- yet another Mie simulator
A Python program with GUI to calculate electromagnetic field enhancement factors for plain-wave and dipole radiation in spherical shell geometry. Additionally, it can calculate the subsequent changes of photophysics for given fluorophores.
# How it works
 Software calculates transfer matrices for electromagnetic field in multipolar expansion for nanoparticles composed of concentric spheres. The method for transfer matrix computation was taken from: [https://doi.org/10.1016/j.aop.2004.07.002](https://doi.org/10.1016/j.aop.2004.07.002). On the basis of that, field enhancement factor for excitation field (with respect to spatially averaged plain-wave) is calculated, the method was adapted from [Le Ru and Etchegoin SPLAC Package](https://www.victoria.ac.nz/scps/research/research-groups/raman-lab/numerical-tools/sers-and-plasmonics-codes). Enhancement of radiative emission rate was calculated as in [https://doi.org/10.1016/j.aop.2004.07.002](https://doi.org/10.1016/j.aop.2004.07.002). Enhancement of total emission rate was obtained by integration of Poynting vector below and under the dipole position.
 The longitudinal modes in nonlocal metal dielectric response were treated as in [https://doi.org/10.1016/j.aop.2004.07.002](https://doi.org/10.1016/j.aop.2004.07.002) with metal hydrodynamic constant and longitudinal wave vector taken as in [https://doi.org/10.1088/0953-8984/27/18/183204](https://doi.org/10.1088/0953-8984/27/18/183204) (omitting the size-correction part). The changes in electron mean-free path due to the surface scattering is obtained from: [https://doi.org/10.1021/jp8010074](https://doi.org/10.1021/jp8010074).
 
 
# Similar software

# Installation
## Running with Python interpreter (recommended)
### Prerequisites
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
### Running
Enter the folder ```yams``` and run:
```bash
cd yams
python3 ./yams.py
```
### Utilizing package components
The following may turn useful for those who might need some scripting. 'The heart' of the package is ```yams/fluoroph1layer2.py``` to which you can pass input files, save name and chosen fluorophores directly. Check more in the comments of  ```yams/fluoroph1layer2.py```.
## Running from binaries (Linux amd64)
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
# Usage
## User interface
## Input files
All input files, as well as settings file are give in ```yaml``` format. Current specifications of the format are given in http://yaml.org/spec/1.2/spec.html. In fact, on the basis of existing files one can create their own without checking ```yaml``` specifications.
### Geometry
Sample geometry files are contained in ```input_files``` folder and it is advised to save the newly created files also there. The files contain all the information needed to compute transfer matrices and enhancement factors. Sample geometry file with comments is in ```input_files/c510test_sample.yaml```. In doubt, you can always save input file generated in GUI by choosing ```file > save input as``` or load the file by ```file >load input file```.
### Photophysics
Photophysics definition files consist of:

* quantum yield,
* orientation of transition dipole moment with respect to radial direction,
* file with emission spectrum.
For detailed specifications please check ```pkg_resources/photophysics/tpp_sample.yaml```. There is no need to add information about photophysics in any other configurations files.

## Output files
Software typically returns output in two formats: ```.pickle``` and ```.mat```. I found ```.txt``` not suitable for large n-dimensional matrices.
### Mie calculation
Output from Mie calculation consist of:

* *param* -- variable with contents of the input,
* *dip_range* -- vector of distances between the dipole and closest inner layer,
* *rho_rel* -- relative density of solvent at provided temperature,
* *results* -- list/cell array of results. Each position in list is a different set of layers sizes from the provided input.

Each result entry consist of:

* *Ca_dict* -- positions of the layers,
* *dip_range* -- absolute positions of the dipole,
* *QabsM*, *QscaM*, *QextM* -- absorption, scattering and extinction efficiencies of the nanoparticle, calculated from backward transfer matrices, as a function of wavelength (in nm),
* *QabsT*, *QscaT*, *QextT* -- absorption, scattering and extinction efficiencies of the nanoparticle, calculated from forward transfer matrices, should in principle be the same as *QabsM*, *QscaM*, *QextM*, 
* *Fexcperp*, *Fexcpara* -- enhancement of the excitation (plane-wave) field for orientations along the radial direction and parallel to nanoparticle surface, respectively. Enhancement factors are averaged over nanoparticle surface.
* *MRadPerp*, *MRadPara* -- radiative part of the enhancement of dipole emission,
* *MTotPerp*, *MTotPara* -- total enhancement of dipole emission, non-radiative energy transfer to the nanoparticle,
* *MNRPerp*, *MNRPara* -- non-radiative part of the enhancement of dipole emission, calculated as *MTot-MRad*.

The shape of enhancement factors matrices is [number of dipole positions] x [number of wavelengths]. The enhancement factors are given with respect to mean incoming plain-wave/dipole field intensity.
### Photophysics
Output of photophysics calculation consists of:

 * *param*, *dip_range*, *rho_rel* as in **Mie calculation**,
 * *QabsM*, *QabsT*, *QextM*, *QextT*, *QscaM*, *QscaT* -- efficiencies matrices reshaped, to ```[layer0 size] x [layer1 size] x ... x [layern size] x [wavelength]``` and multiplied by *rho_rel* to express the observed changes in the spectra,
 * *Fexc_fluorophore* -- excitation enhancement for orientation of given fluorophore, reshaped to ```[layer0 size] x ... x [layern size] x [dipole positions] x [wavelength]```. This should give the change of exciation spectrum.
 * *Frad_fluorophore* -- radiative decay rate enhancement as a function of emission wavelength, for given fluorophore orientation, the same size as *Fexc_fluorophore*. This should give the change of emission spectrum shape.
 * *FkRad_fluorophore* -- radiative decay rate enhancement integrated over fluorophore emission spectrum, the shape is: ```[layer0 size] x ... x [layern size] x [dipole positions]```,
 * *FkTot _fluorophore* -- total decay rate enhancement integrated over fluorophore emission spectrum, the shape is as in *FkRad_fluorophore*,
 * *Ftau_fluorophore* -- reduction of fluorophore excited state lifetime, taking into account *FkTot _fluorophore* and its intrinsic non-radiative decay rate,
 * *FQY_fluorophore* -- enhancement of fluorophore quantum yield, *FkRad* * *Ftau*,
 * *FGamma_fluorophore* -- enhancement of the observed fluorophore emission, *Fexc* * *FQY*.
 
 Additionally, plots for chosen wavelengths for *Fexc*, *Frad*, *FGamma* and for *Ftau* and *FQY* are generated. They are meant to provide quick insight into the results rather than serve as publication-ready figures. The plotting can be switched off in ```pkg_resources/settings.yaml```, where you can also change the chosen wavelengths.
## Advanced
### Settings
Advanced settings are in ```pkg_resources/setting.yaml```. These include multiprocessing, vector spherical harmonics (VSH) series truncation in case on non-convergence and plotting options. Check comments of ```pkg_resources/setting.yaml```.
### Adding refractive index

1. Prepare .txt file with complex refractive index as a function of wavelength (in nm). Put the file in ```pkg_resources/ref_ind``` directory.
2. Add entry to ```pkg_resources/materials.yaml```:
```yaml
material:
	file: file_without_txt_extension	# file with refractive index
							# location: resources/ref_ind/file_without_txt_extension.txt
							# first column in wavelength in nm
							# second column is complex refractive index
							# the field cannot be empty
	ref: key_of_reference	# reference to paper with published refractive index
							# key in pkg_resources/references/RI.bib
							# the field can be left empty
```
3. (Optional) Add reference entry to ```pkg_resources/references/RI.bib```.
### Adding corrections for metal
Corrections for metal include:

* correction for surface scattering of electrons (limited mean-free path),
* correction for temperature to dielectric function.
* correction for lonlocality of dielectric function.

Corrections can be included by adding appropriate entry in ```pkg_resources/mat_sizecor.yaml```. Entry consist of material constants in the right units, check comments in ```pkg_resources/mat_sizecor.yaml```. 
### Adding temperature correction for medium
Solvents increase their density and refractive index with decreasing temperature. The changes in refractive index are calculated basing on density changes using Eyckmann's formula, check eq. (2) in [10.1111/j.1751-1097.1973.tb06343.x](10.1111/j.1751-1097.1973.tb06343.x).
To include temperature changes on refractive index one needs the relative (to 298 K) densities of the solvents for each temperature. The file consist of a column with temperatures (in Kelvin) and a column with relative densities. Location of the files in ```pkg_resources/rho```. New entry for the solvent should be made in ```pkg_resources/mat_tempcor.yaml``` (just like in  ```pkg_resources/materials.yaml```).
# Credits
Contact: annamariakelm@gmail.com, GitHub: https://github.com/akelm

# How to cite
Kelm, A. (2017). YAMS -- yet another Mie simulator [Computer software]. Available from: https://github.com/akelm/YAMS
[BibTeX file](pkg_resources/references/citeme.bib)
# References

# License
Copyright (C) 2017 Anna Kelm

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

[License file](LICENCSE)