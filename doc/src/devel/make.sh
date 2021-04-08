#!/bin/sh -x
#set -x
#export PS4='+ l.${LINENO}: ${FUNCNAME[0]:+${FUNCNAME[0]}(): }'
sh -x ./clean.sh

function system {
# Run operating system command and if failure, report and abort

  "$@"
  if [ $? -ne 0 ]; then
    echo "make.sh: unsuccessful command $@"
    echo "abort!"
    exit 1
  fi
}

# html
system doconce format html development  --html_style=bootswatch_readable --html_code_style=inherit --no_abort --no_mako


dest=../../pub/devel
#rm -rf $dest/html
rm -rf $dest/development.html
cp development.html $dest


echo "To remove untracked files run:"
echo "git clean -f -d"