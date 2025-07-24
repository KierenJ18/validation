#!/bin/bash
EVENT_DIR=$1
ANALYSIS_FILE=$2
BRANCH=$3
OUT_DIR=$4
if [ $# -lt 1 ]; then
	echo "Usage: $0 <event_dir> <analysis_file> <branch_type> <output_dir>"
        return 2
fi

cd $1;
for branch in $3; do
    for file in *.root; do
       $2 $file 0 $branch $4
    done
done

echo "Analysis completed successfully."
