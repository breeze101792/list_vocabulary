#!/bin/bash
function dict_init()
{
    local cpath=`pwd`
    local dict_file=$cpath/third_party/ecdict/stardict.7z
    local work_tmp="/tmp/pydict"
    local target_dictionary_path="${HOME}/.config/list_vocbs/dictionary"
    mkdir $work_tmp
    pushd $work_tmp
    {
        7z x $dict_file
        # ignore convert, choose the supported terminal instead.
        # iconv -sc -f utf8 -t gb2312 stardict.csv | iconv -sc -f gb2312 -t big5 | iconv -sc -f big5 -t utf8 > stardict_t.csv
        cp stardict.csv stardict_t.csv
        python3 $cpath/ecdict_convert.py secdict.db stardict_t.csv
        cp secdict.db ${target_dictionary_path}
    }
    popd
}
function generate_exc()
{
    local exc_file='pydict'
    local cpath=`pwd`
    echo "#!/bin/bash" > $exc_file
    echo "pushd $cpath > /dev/null" > $exc_file
    echo "source .venv/bin/activate" > $exc_file
    echo "python3 $cpath/pydict.py \$@" >> $exc_file
    echo "popd > /dev/null" > $exc_file

    # #!/bin/bash
    # pushd /Users/shaowu/projects/list_vocabulary/ > /dev/null
    #
    # source .venv/bin/activate
    #
    # python3 /Users/shaowu/projects/list_vocabulary/pydict.py $@
    #
    # popd > /dev/null
    chmod u+x $exc_file
}

function fHelp()
{
    echo "Setup Usage"
    printf "    %s%s%s\n" "-d|--dict" "->" "Setup dict db"
    printf "    %s%s%s\n" "-e|--exec" "->" "generate exec file"
    printf "    %s%s%s\n" "-h|--help" "->" "Help me"
    echo "Note."
    echo "      Step 1. Do submodule init/update"
    echo "      Step 2. Install p7zip-full, iconv, pyton3."
}
function fPKGCheck()
{
    if ! command -v iconv
    then
        echo "Iconv not found, please install it"
    fi

    if ! command -v 7z
    then
        echo "p7zip-full not found, please install it"
    fi
}

function setup()
{
    while [ "$#" != "0" ]
    do
        case $1 in
            -d|--dict)
                dict_init
                ;;
            -e|--exec)
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
