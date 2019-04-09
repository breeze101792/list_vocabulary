function dict_init()
{
    local cpath=`pwd`
    local dict_file=$cpath/third_party/ecdict/stardict.7z
    local work_tmp="/tmp/pydict"
    mkdir $work_tmp
    pushd $work_tmp
    {
        7z x $dict_file
        python $cpath/ecdict.py dict.db stardict.csv
        cp dict.db $cpath
    }
    popd
}
function generate_exc()
{
    local exc_file='pydict'
    local cpath=`pwd`
    echo "#!/bin/bash" > $exc_file
    echo "python3 $cpath/main.py $@" > $exc_file
    chmod u+x $exc_file
}
if [ ! -f dict.db ]
then
    dict_init
fi
generate_exc
