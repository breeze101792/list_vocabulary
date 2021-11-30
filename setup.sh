#!/bin/bash
function dict_init()
{
    local cpath=`pwd`
    local dict_file=$cpath/third_party/ecdict/stardict.7z
    local work_tmp="/tmp/pydict"
    mkdir $work_tmp
    pushd $work_tmp
    {
        7z x $dict_file
        iconv -f utf8 -t gb2312 stardict.csv | iconv -f gb2312 -t big5 | iconv -f big5 -t utf8 > stardict_t.csv
        python3 $cpath/ecdict.py dict.db stardict*csv
        cp dict.db $cpath
    }
    popd
}
function generate_exc()
{
    local exc_file='pydict'
    local cpath=`pwd`
    echo "#!/bin/bash" > $exc_file
    echo "python3 $cpath/main.py \$@" >> $exc_file
    chmod u+x $exc_file
}

function fHelp()
{
    echo "Setup Usage"
    printf "    %s%s%s\n" "-d|--dict" "->" "Setup dict db"
    printf "    %s%s%s\n" "-h|--help" "->" "Help me"
    echo "Note."
    echo "      Step 1. Do submodule init/update"
    echo "      Step 2. Install p7zip-full, iconv, pyton3."
}

function setup()
{
    while [ "$#" != "0" ]
    do
        case $1 in
            -d|--dict)
                dict_init
                generate_exc
                ;;
            -h|--help)
                fHelp
                return 0
                ;;
            *)
                echo "Unknown Args"
                fHelp
                return 1
                ;;
        esac
        shift 1
    done
}
setup $@
