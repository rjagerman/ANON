#!/bin/sh

# Name
python generate_readme.py -l -s name -o TABLE_NAME.md
# LOC
python generate_readme.py -r -l -s total_code_lines -o TABLE_LOC.md
# Contributors
python generate_readme.py -r -l -s total_contributor_count -o TABLE_CONTRIBUTORS.md
# Last activity
python generate_readme.py -r -l -s updated_at -o TABLE_LAST_ACTIVITY.md
