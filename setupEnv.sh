# Necessary for allowing modules to import sibling modules
THISPATH="$( dirname "$(readlink -f -- "$0")" )"
echo "Prepending PYTHONPATH with $THISPATH"
export PYTHONPATH=$THISPATH:$PYTHONPATH
