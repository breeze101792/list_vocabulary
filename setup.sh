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
dict_init
