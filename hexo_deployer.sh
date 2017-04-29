#!/bin/sh

echo hexo deployer processing...
PATH=$PATH:/usr/local/bin
PATH=$PATH:/usr/bin
echo $PATH
hexo clean
hexo g
hexo d