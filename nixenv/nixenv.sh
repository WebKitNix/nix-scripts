function nixenv() {
    BASESOURCESDIR=$HOME/work
    WEBKITWORKDIR=nix
    WKBUILD=Release
    if [ "$1" ]
    then
        WEBKITWORKDIR=$1
    fi
    if [ "$2" ]
    then
        WKBUILD=$2
    fi

    export WEBKITSOURCEDIR=$BASESOURCESDIR/$WEBKITWORKDIR
    export WEBKITOUTPUTDIR=$BASESOURCESDIR/$WEBKITWORKDIR-build
    export WEBKITINSTALLDIR=$BASESOURCESDIR/$WEBKITWORKDIR-install

    if [ ! $ORIGINAL_PATH ]; then
        export ORIGINAL_PATH=$PATH
        export ORIGINAL_LIBRARY_PATH=$LIBRARY_PATH
        export ORIGINAL_LD_LIBRARY_PATH=$LD_LIBRARY_PATH
        export ORIGINAL_PKG_CONFIG_PATH=$PKG_CONFIG_PATH
    fi

    unset PATH
    unset LIBRARY_PATH
    unset LD_LIBRARY_PATH
    unset PKG_CONFIG_PATH

    export ICECC_CC=/usr/bin/gcc
    export PATH=/usr/lib/icecc/bin/:$WEBKITSOURCEDIR/Tools/Scripts:$WEBKITOUTPUTDIR/$WKBUILD/bin:$WEBKITOUTPUTDIR/Dependencies/Root/bin:$WEBKITINSTALLDIR/bin:$ORIGINAL_PATH
    export LIBRARY_PATH=$WEBKITOUTPUTDIR/$WKBUILD/lib:$WEBKITINSTALLDIR/lib:$WEBKITOUTPUTDIR/Dependencies/Root/lib64:$ORIGINAL_LIBRARY_PATH
    export LD_LIBRARY_PATH=$WEBKITOUTPUTDIR/$WKBUILD/lib:$WEBKITINSTALLDIR/lib:$WEBKITOUTPUTDIR/Dependencies/Root/lib64:$ORIGINAL_LD_LIBRARY_PATH
    export PKG_CONFIG_PATH=$WEBKITOUTPUTDIR/$WKBUILD/lib/pkgconfig:$WEBKITINSTALLDIR/lib/pkgconfig:$WEBKITOUTPUTDIR/Dependencies/Root/lib64/pkgconfig:$ORIGINAL_PKG_CONFIG_PATH

    #export GST_PLUGIN_PATH=$WEBKITOUTPUTDIR/Dependencies/Root/lib64/gstreamer-1.0:$GST_PLUGIN_PATH
    #export GST_PLUGIN_SYSTEM_PATH=$WEBKITOUTPUTDIR/Dependencies/Root/lib64/gstreamer-1.0:$GST_PLUGIN_SYSTEM_PATH
}

function nixbuild() {
    if [ $WEBKITSOURCEDIR ]; then
        if [ "$1" ]
        then
            FLAGS=$1
        fi
        cd $WEBKITSOURCEDIR
        rm -rf $WEBKITOUTPUTDIR/$WKBUILD
        Tools/Scripts/build-webkit --nix --${WKBUILD,,} --makeargs="-j80" --prefix=$WEBKITINSTALLDIR $FLAGS
    else
        echo "[ERROR] Please set the nix environment."
    fi
}

function nixtest() {
    if [ $WEBKITSOURCEDIR ]; then
        cd $WEBKITSOURCEDIR
        Tools/Scripts/new-run-webkit-tests --nix --no-retry-failures --fully-parallel --no-show-results --no-new-test-results --no-ref-tests --no-pixel-tests $*
    else
        echo "[ERROR] Please set the nix environment."
    fi
}

function nixmake() {
    if [ $WEBKITSOURCEDIR ]; then
        if [ "$1" ]
        then
            FLAGS=$1
        fi
        cd $WEBKITOUTPUTDIR/$WKBUILD
        make -j80 ; cd -
    fi
}

function nixinstall() {
    if [ $WEBKITSOURCEDIR ]; then
        cd $WEBKITOUTPUTDIR/Release
        make install/fast
    fi
}

function gtkenv() {
    BASESOURCESDIR=$HOME/garden
    WEBKITWORKDIR=gtkwebkit
    WKBUILD=Release
    if [ "$1" ]
    then
        WEBKITWORKDIR=$1
    fi
    if [ "$2" ]
    then
        WKBUILD=$2
    fi

    export WEBKITSOURCEDIR=$BASESOURCESDIR/$WEBKITWORKDIR
    export WEBKITOUTPUTDIR=$BASESOURCESDIR/$WEBKITWORKDIR-build
    export WEBKITINSTALLDIR=$BASESOURCESDIR/$WEBKITWORKDIR-install

    if [ ! $ORIGINAL_PATH ]; then
        export ORIGINAL_PATH=$PATH
        export ORIGINAL_LIBRARY_PATH=$LIBRARY_PATH
        export ORIGINAL_LD_LIBRARY_PATH=$LD_LIBRARY_PATH
        export ORIGINAL_PKG_CONFIG_PATH=$PKG_CONFIG_PATH
    fi

    unset PATH
    unset LIBRARY_PATH
    unset LD_LIBRARY_PATH
    unset PKG_CONFIG_PATH

    export ICECC_CC=/usr/bin/gcc
    export PATH=/usr/lib/icecc/bin/:$WEBKITSOURCEDIR/Tools/Scripts:$WEBKITOUTPUTDIR/$WKBUILD/bin:$WEBKITOUTPUTDIR/Dependencies/Root/bin:$WEBKITINSTALLDIR/bin:$ORIGINAL_PATH
    export LIBRARY_PATH=$WEBKITOUTPUTDIR/$WKBUILD/lib:$WEBKITINSTALLDIR/lib:$WEBKITOUTPUTDIR/Dependencies/Root/lib64:$ORIGINAL_LIBRARY_PATH
    export LD_LIBRARY_PATH=$WEBKITOUTPUTDIR/$WKBUILD/lib:$WEBKITINSTALLDIR/lib:$WEBKITOUTPUTDIR/Dependencies/Root/lib64:$ORIGINAL_LD_LIBRARY_PATH
    export PKG_CONFIG_PATH=$WEBKITOUTPUTDIR/$WKBUILD/lib/pkgconfig:$WEBKITINSTALLDIR/lib/pkgconfig:$WEBKITOUTPUTDIR/Dependencies/Root/lib64/pkgconfig:$ORIGINAL_PKG_CONFIG_PATH
}
