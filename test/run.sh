set -e
wget baidu.com -P ../data/HMM
#wget https://raw.githubusercontent.com/fxsjy/jieba/master/jieba/dict.txt -P ../data/HMM

# https://docs.travis-ci.com/user/environment-variables/#default-environment-variables
# TRAVIS=TRUE
if test $TRAVIS
then
    source $HOME/miniconda/etc/profile.d/conda.sh
    conda activate py3torch-cpu
fi

for file in ./*.py
do
	python $file
done
