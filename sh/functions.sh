#! /not/to/be/execed
# Intended to be loaded into the current shell (e.g. with the "source" or "." command).

access() {
    # mount point for encrypted file system
    local ACCESS_MNT=~/mnt
    
    # data file
    local ACCESS_TXT=~/mnt/access.txt
    
    # mount if not already mounted (no file $ACCESS_TXT)
    [[ -f $ACCESS_TXT ]] || encfs --idle=3 ~/secret $ACCESS_MNT
    
    # print lines around those containing search word
    grep -iA5 "$1" $ACCESS_TXT    
}

delpath() {
    addpath -d "$@"
}

addpath() {
    local USAGE="Usage: $FUNCNAME [-h|-a|-d] [-p <path>] <dir> [<dir> ...]
-h   help, print this message to stderr
-a   append <dir>s to <path> (default is to prepend)
-d   delete <dir>s from <path> (delpath is equivalent to addpath -d)
-p   name of path variable to be updated (default is PATH)
-f   allow <dir> to be a file or a dir"

    local HINT="\nTry -h for help."

    # name of path variable we modify
    local path='PATH'
    
    # Boolean options
    local append=0 # prepend by default
    local delete=0 # add by default
    local file=0   # only dirs accepted by default

    # handle options
    OPTIND=1
    local opt
    while getopts :hadp:f opt; do
    	case $opt in
	h)  echo -e "$USAGE" >&2
    	    return 1
	    ;;
	a)  append=1
    	    ;;
	d)  delete=1
	    ;;
	p)  path="$OPTARG"
    	    ;;
	f)  file=1
	    ;;
	*)  echo -e "Unexpected option: $OPTARG.$HINT" >&2
    	    return 2
	    ;;
	esac
    done
    
    if [[ "$append" = 1 ]] && [[ "$delete" = 1 ]]; then
    	echo -e "Contradictory options: -a for append can't be used with -d for delete.$HINT" >&2
    	return 3
    fi

    if [[ $OPTIND -gt $# ]]; then
        echo -e "Missing <dir>.$HINT" >&2
    	return 3
    fi
    
    # current path value
    eval local val=\$$path
    
    while [[ $OPTIND -le $# ]]; do
    eval local dir=\${$OPTIND}
	# echo "OPTIND = $OPTIND, dir = $dir"
    
	# update val to new path value
	if [[ "$delete" = 1 ]]; then
    
    	    if echo "$val" | egrep -v "(^|:)$dir(:|$)" >/dev/null 2>&1; then
	    	echo -e "Path $path=$val does not contain <dir>=$dir.$HINT" >&2
		return 4
	    fi
	
	    val=`echo "$val" | sed -E -e "s~(^|:)$dir:~\1~g" -e "s~:$dir(:|$)~\1~g" -e "s~^$dir$~~g"`
	
	else
    
	    [[ $file == 1 ]] || [[ -d "$dir" ]] || {
		echo -e "<dir>=$dir is not a directory.$HINT" >&2
		return 5
	    }
	    
	    if [ "X$val" = "X" ]; then
		val=$dir
	    else
		if echo "$val" | egrep "(^|:)$dir(:|\$)" >/dev/null 2>&1; then
		    echo -e "Path already contains $dir. $path=$val" >&2
		else
		    if [[ "$append" = 1 ]]; then
			val="$val:$dir"
		    else
			val="$dir:$val"
		    fi
		fi
	    fi
        fi
	
	OPTIND=$(($OPTIND + 1))
    done
    
    # set new path value
    eval $path="\$val"
}

sedit() {
    # Possible enhancements:
    # - let user change the ~ delimeter incase it appears in $find or $replace
    # - allow use of complex RE's with sed -E
    
    local USAGE="Usage: $FUNCNAME <find> <replace> <file> [<file>...]
Uses sed to perform global substitutions in multiple files.
<find>    the (simple) regular expression (RE) to be replaced
<replace> the replacement text (possibly with back refs to groups in <find>)
<file>... the files to be edited (original content is saved in *.bak)"
    
    if [[ $# -lt 3 ]]; then
        echo -e "$USAGE" >&2
	return 1
    fi
    
    local find="$1"
    local replace="$2"
    shift 2
    local file
    for file in "$@"; do
        echo -n "Editing $file..."
	local bak="$file".bak
	mv "$file" "$bak"
	if sed "s~$find~$replace~g" "$bak" > $file; then
	    echo " done."
	else
	    echo " error."
	    mv "$bak" "$file"
	fi
    done
}
