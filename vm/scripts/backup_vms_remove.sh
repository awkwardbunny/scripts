#!/bin/bash
cd /vm/backups
# delete backups older than 60 days
find . -mtime +60 -print0 | xargs -r0 -- rm -r
