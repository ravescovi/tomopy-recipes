Tomopy Recipes
##############

Example recipes for the new conda build system. Use::

    conda build <recipe directory>

We suggest that the correct order should be:

::

    #download anaconda for linux64bits
    wget http://repo.continuum.io/archive/Anaconda2-4.0.0-Linux-x86_64.sh
    bash Anaconda2-4.0.0-Linux-x86_64.sh #this will ask for ok
    conda update --yes --all
    
    git clone https://github.com/ravescovi/tomopy-recipes.git
    cd tomopy-recipes/
    conda build tifffile/.
    conda install --yes --use-local tifffile --force
    conda build edffile/.
    conda install --yes --use-local edffile --force
    conda build spefile/.
    conda install --yes --use-local spefile --force
    conda build dxfile/.
    conda install --yes --use-local dxfile --force
    conda build olefile/.
    conda install --yes --use-local olefile --force
    conda build data-exchange/.
    conda install --yes --use-local dxchange --force
    conda build tomopy/. 
    conda install --yes --use-local tomopy --force
    conda build astra/.
    conda install --yes --use-local astra-toolbox --force
    cd ..

This project ('tomopy-recipes') is in the public domain. Note that this 
statement does not reflect in any way, shape or form the licenses of the
projects which are being built from these recipes. For example, even
though a project `foo` might have an MIT, Apache, or any other license,
the recipe for project `foo` (within this repository) is public domain.
